from __future__ import annotations

import socket
import sys


def port_is_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) != 0


def main() -> int:
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    for port in range(start, start + 50):
        if port_is_open(host, port):
            print(port)
            return 0
    print(start)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
