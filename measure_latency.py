#!/usr/bin/env python3
"""Медиана round-trip локальных калькулятор-клиентов (с запуском Python)."""
import argparse
import statistics
import subprocess
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument('--mode', choices=['fifo', 'unix'], required=True)
parser.add_argument('--path', required=True)
parser.add_argument('--repeats', type=int, default=10)
args = parser.parse_args()
if args.repeats <= 0:
    parser.error('repeats >= 1')
cmd = ([sys.executable, 'fifo_client.py', '12*(3+4)', '--dir', args.path]
       if args.mode == 'fifo' else
       [sys.executable, 'unix_client.py', '12*(3+4)', '--socket', args.path])
results = []
for i in range(args.repeats):
    start = time.perf_counter()
    subprocess.run(cmd, stdout=subprocess.DEVNULL, check=True)
    results.append(time.perf_counter() - start)
print(f'{args.mode}: 1 короткий запрос/ответ (~сотни байт), '
      f'медиана {args.repeats} повторов = {statistics.median(results):.5f} с')
print('Сюда включён запуск Python-клиента; сравнение с 40 MiB Pipe/SharedMemory не прямое.')
