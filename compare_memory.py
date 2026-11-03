#!/usr/bin/env python3
"""Передача 10**7 uint32: shared_memory vs Pipe (с проверкой контрольной суммы)."""
import argparse
from array import array
import multiprocessing as mp
from multiprocessing import shared_memory
import time


def pipe_receiver(conn, ack):
    try:
        blob = conn.recv_bytes()
        numbers = array('I')
        numbers.frombytes(blob)
        ack.send((len(numbers), sum(numbers)))
    finally:
        conn.close()
        ack.close()


def shm_receiver(name, count, ack):
    mem = shared_memory.SharedMemory(name=name)
    try:
        view = mem.buf.cast('I')
        try:
            ack.send((len(view), sum(view)))
        finally:
            view.release()
    finally:
        mem.close()
        ack.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=10_000_000)
    args = parser.parse_args()
    if args.count < 1:
        parser.error('count >= 1')
    values = array('I', (i % 100 for i in range(args.count)))
    assert values.itemsize == 4
    blob = values.tobytes()
    expected = (len(values), sum(values))
    ctx = mp.get_context('spawn')

    recv, send = ctx.Pipe(duplex=False)
    result_recv, result_send = ctx.Pipe(duplex=False)
    proc = ctx.Process(target=pipe_receiver, args=(recv, result_send))
    start = time.perf_counter()
    proc.start()
    recv.close(); result_send.close()
    send.send_bytes(blob)
    answer = result_recv.recv()
    proc.join()
    pipe_time = time.perf_counter() - start
    send.close(); result_recv.close()
    assert proc.exitcode == 0 and answer == expected

    mem = shared_memory.SharedMemory(create=True, size=len(blob))
    try:
        mem.buf[:len(blob)] = blob
        recv, send = ctx.Pipe(duplex=False)
        proc = ctx.Process(target=shm_receiver, args=(mem.name, args.count, send))
        start = time.perf_counter()
        proc.start()
        send.close()
        answer = recv.recv()
        proc.join()
        shm_time = time.perf_counter() - start
        recv.close()
        assert proc.exitcode == 0 and answer == expected
    finally:
        mem.close()
        mem.unlink()
    print(f'Чисел: {args.count:,}; размер: {len(blob)/1024/1024:.2f} MiB')
    print('Механизм          Sync           Объём       Время (с)')
    print(f'Pipe               IPC/receive    {len(blob)/1024/1024:8.2f} MiB {pipe_time:10.4f}')
    print(f'SharedMemory       сигнал Pipe    {len(blob)/1024/1024:8.2f} MiB {shm_time:10.4f}')
    print('Для SharedMemory выделение/заполнение массива сделано до таймера: сравниваем доступ к подготовленным данным.')
    print('Оба таймера включают запуск процесса и подсчёт суммы. Время зависит от среды и размеров /dev/shm.')


if __name__ == '__main__':
    main()
