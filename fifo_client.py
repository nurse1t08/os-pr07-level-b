#!/usr/bin/env python3
"""Клиент: запрос через один FIFO, ответ через отдельный FIFO."""
import argparse
import json
import os
from pathlib import Path
import tempfile


def main():
    p = argparse.ArgumentParser()
    p.add_argument('expression')
    p.add_argument('--dir', default='/tmp/pr07-ipc')
    args = p.parse_args()
    server = Path(args.dir).resolve() / 'requests.fifo'
    with tempfile.TemporaryDirectory(prefix='pr07-client-') as temp:
        reply_path = Path(temp) / 'reply.fifo'
        os.mkfifo(reply_path, 0o600)
        data = (json.dumps({'expr': args.expression, 'reply': str(reply_path)}) + '\n').encode()
        if len(data) > 4096:
            raise SystemExit('Слишком большой запрос')
        fd = os.open(server, os.O_WRONLY)
        try:
            os.write(fd, data)  # единичная атомарная короткая запись в FIFO
        finally:
            os.close(fd)
        with reply_path.open(encoding='utf-8') as stream:
            print(json.loads(stream.readline()))


if __name__ == '__main__':
    main()
