#!/usr/bin/env python3
"""visca-bridge main module

Single-process VISCA-over-TCP -> RS232 bridge optimized for small systems
(Raspberry Pi notes in README.md). This module is intentionally simple:
- loads optional .env from repo root (see `load_env_file`)
- chooses a serial port (interactive when running in a TTY)
- starts a non-blocking TCP server on VISCA_IP_PORT and proxies bytes

The code uses a background thread (`visca_loop`) and a select()-based
main loop for client sockets. Shutdown is cooperative via the global
`running` flag.
"""

from time import sleep
from threading import Thread

from visca.config import load_env_file, SERIAL_PORT
from visca.logging import log
from visca.serial_bridge import setup_serial, serial_conn
from visca.tcp_server import (
    setup_visca_server,
    visca_loop,
    visca_socket,
    clients,
)
import visca.tcp_server as tcp_server


# Load .env early so environment variables and module-level defaults
# (eg. SERIAL_PORT) can pick up configured values from the repository.
load_env_file()


def main() -> None:
    """Entry point: open serial, start TCP server and run until SIGINT.

    The process exits early if the serial port or TCP server fail to start.
    For non-interactive environments set VISCA_SERIAL_PORT in the environment
    to avoid prompts.
    """
    print("=" * 40)
    print("VISCA Bridge - CV620 Edition (FIXED)")
    print("=" * 40)

    if not setup_serial():
        print("ERROR: Serial port cannot be opened")
        print(f"Check: sudo chmod 666 {SERIAL_PORT}")
        return

    if not setup_visca_server():
        print("ERROR: VISCA server cannot be started")
        return

    # Set the global running flag in tcp_server module
    tcp_server.running = True

    # Start VISCA thread
    visca_thread = Thread(target=visca_loop, daemon=True)
    visca_thread.start()

    try:
        while tcp_server.running:
            sleep(1)
    except KeyboardInterrupt:
        print("\nShutdown...")
        tcp_server.running = False
        if serial_conn:
            serial_conn.close()
        if visca_socket:
            visca_socket.close()
        for client in clients:
            try:
                client.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()
