#!/usr/bin/env python3
"""Unix domain socket: отдельный fork-процесс на каждого клиента."""
import argparse
import json
import os
from pathlib import Path
import signal
import socketserver
from calculator import response


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        line = self.rfile.readline(4096)
        try:
            expression = json.loads(line)['expr']
            result = response(expression)
        except (ValueError, KeyError, TypeError) as exc:
            result = {'error': str(exc)}
        self.wfile.write((json.dumps({'server_pid': os.getpid(), **result}) + '\n').encode())


class Server(socketserver.ForkingMixIn, socketserver.UnixStreamServer):
    max_children = 20


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--socket', default='/tmp/pr07-calc.sock')
    args = p.parse_args()
    path = Path(args.socket).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise SystemExit(f'Путь занят: {path}')
    def stop(*_):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, stop)
    with Server(str(path), Handler) as server:
        print(f'Unix socket сервер PID={os.getpid()}, адрес={path}', flush=True)
        try:
            server.serve_forever(poll_interval=0.1)
        except KeyboardInterrupt:
            pass
        finally:
            path.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
