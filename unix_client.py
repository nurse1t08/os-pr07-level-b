#!/usr/bin/env python3
import argparse
import json
import socket

p = argparse.ArgumentParser()
p.add_argument('expression')
p.add_argument('--socket', default='/tmp/pr07-calc.sock')
args = p.parse_args()
with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
    sock.connect(args.socket)
    sock.sendall((json.dumps({'expr': args.expression}) + '\n').encode())
    print(json.loads(sock.makefile().readline()))
