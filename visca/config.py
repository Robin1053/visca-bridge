"""Configuration management for VISCA Bridge.

Handles loading environment variables from .env file,
port selection, and global configuration constants.
"""

import os
import sys
from pathlib import Path
from serial.tools import list_ports


def load_env_file() -> None:
    """Load a simple .env file from the project root.

    Important: values are installed into os.environ using
    `os.environ.setdefault(key, value)`. That means real environment
    variables take precedence over `.env` entries. Use explicit
    environment variables when running in automation/CI.
    """
    env_path = Path(__file__).parent.parent / '.env'
    if not env_path.exists():
        return

    with env_path.open('r', encoding='utf-8') as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue

            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            if value and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]

            if key:
                os.environ.setdefault(key, value)


def list_serial_ports() -> list:
    """List all available serial ports on the system.

    Returns:
        list: List of serial.tools.list_ports.ListPortInfo objects
    """
    return list(list_ports.comports())


def choose_serial_port(default_port: str = None) -> str:
    """Interactively choose a serial port if multiple are available.

    If VISCA_SERIAL_PORT environment variable is set, that port is used
    immediately without prompting.

    Args:
        default_port: Default port to use if none is selected (default: /dev/ttyUSB0)

    Returns:
        str: Path to the selected serial port
    """
    if default_port is None:
        default_port = os.getenv('VISCA_SERIAL_PORT', '/dev/ttyUSB0')

    # If environment variable is explicitly set, use it immediately
    configured_port = os.getenv('VISCA_SERIAL_PORT')
    if configured_port:
        return configured_port

    ports = list_serial_ports()

    if not ports:
        # No serial devices found: use default. This is common in CI
        # or headless containers where no /dev/ttyUSB* exists.
        print(f"No serial devices found, using default port: {default_port}")
        return default_port

    print('\nAvailable serial ports:')
    for index, port in enumerate(ports, start=1):
        description = port.description or 'unknown'
        manufacturer = f' | {port.manufacturer}' if port.manufacturer else ''
        print(f"  {index}) {port.device} - {description}{manufacturer}")

    # If not running in an interactive TTY (daemon/CI), don't attempt to
    # prompt the user; fall back to the default. Automated runs should set
    # VISCA_SERIAL_PORT to avoid surprises.
    if not sys.stdin.isatty():
        print(f"No interactive terminal, using default port: {default_port}")
        return default_port

    while True:
        try:
            choice = input(f"\nSelect device [1-{len(ports)}] or press Enter for {default_port}: ").strip()
            if choice == '':
                return default_port

            selected_index = int(choice) - 1
            if 0 <= selected_index < len(ports):
                return ports[selected_index].device

            print('Invalid selection.')
        except ValueError:
            print('Please enter a valid number.')


# Load .env early so environment variables can be read
load_env_file()

# Configuration Constants
VISCA_IP_HOST = '0.0.0.0'
VISCA_IP_PORT = 1259

SERIAL_PORT = os.getenv('VISCA_SERIAL_PORT', '/dev/ttyUSB0')
SERIAL_BAUDRATE = int(os.getenv('VISCA_SERIAL_BAUDRATE', '9600'))
SERIAL_TIMEOUT = 1.0
RESPONSE_WAIT = 0.3

MAX_LOG_ENTRIES = 100
