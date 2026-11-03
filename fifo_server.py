#!/usr/bin/env python3
"""Сервис по FIFO, запросы обрабатываются по очереди."""
import argparse
import json
import os
import signal
from pathlib import Path
from calculator import response


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--dir', default='/tmp/pr07-ipc')
    args = p.parse_args()
    folder = Path(args.dir).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / 'requests.fifo'
    if path.exists():
        raise SystemExit(f'FIFO уже существует: {path} (запущен другой сервер?)')
    os.mkfifo(path, 0o600)
    def stop(*_):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, stop)
    print(f'FIFO сервер слушает: {path}', flush=True)
    try:
        # O_RDWR предотвращает EOF между последовательно подключающимися клиентами (Linux).
        fd = os.open(path, os.O_RDWR)
        with os.fdopen(fd, 'r', encoding='utf-8') as stream:
            for line in stream:
                try:
                    req = json.loads(line)
                    result = response(req['expr'])
                    with open(req['reply'], 'w', encoding='utf-8') as reply:
                        reply.write(json.dumps(result) + '\n')
                except (OSError, ValueError, KeyError, TypeError) as exc:
                    print('Ошибка запроса:', exc, flush=True)
    except KeyboardInterrupt:
        print('\nFIFO сервер остановлен.')
    finally:
        path.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
