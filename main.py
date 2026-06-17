#!/usr/bin/env python3
"""visca-bridge main module

Single-file VISCA-over-TCP -> RS232 bridge optimized for small systems
(Raspberry Pi notes in README.md). This module is intentionally simple:
- loads optional .env from repo root (see `load_env_file`)
- chooses a serial port (interactive when running in a TTY)
- starts a non-blocking TCP server on VISCA_IP_PORT and proxies bytes

The code uses a background thread (`visca_loop`) and a select()-based
main loop for client sockets. Shutdown is cooperative via the global
`running` flag.
"""

import socket
import serial
from serial.tools import list_ports
import select
import json
import os
import sys
from pathlib import Path
from time import time, sleep
from collections import deque
from threading import Thread, Lock
from urllib.parse import urlparse


# Konfiguration
VISCA_IP_HOST = '0.0.0.0'
VISCA_IP_PORT = 1259


def load_env_file():
    """Load a simple .env file from the project root.

    Important: values are installed into os.environ using
    `os.environ.setdefault(key, value)`. That means real environment
    variables take precedence over `.env` entries. Use explicit
    environment variables when running in automation/CI.
    """
    env_path = Path(__file__).with_name('.env')
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


# Load .env early so environment variables and module-level defaults
# (eg. SERIAL_PORT) can pick up configured values from the repository.
load_env_file()

SERIAL_PORT = os.getenv('VISCA_SERIAL_PORT', '/dev/ttyUSB0')
SERIAL_BAUDRATE = int(os.getenv('VISCA_SERIAL_BAUDRATE', '9600'))
SERIAL_TIMEOUT = 1.0
MAX_LOG_ENTRIES = 100
RESPONSE_WAIT = 0.3

# Globale Variablen
serial_conn = None
visca_socket = None
clients = []
stats = {
    'start_time': int(time()),
    'clients': 0,
    'total_conn': 0,
    'ip_to_rs232': 0,
    'rs232_to_ip': 0,
    'last_activity': 0
}
log_queue = deque(maxlen=MAX_LOG_ENTRIES)
log_lock = Lock()
running = True


def log(level, msg):
    """Logging mit Thread-Safety"""
    with log_lock:
        entry = {'t': int(time()), 'l': level[0], 'm': msg}
        log_queue.appendleft(entry)
        timestamp = time()
        print(f"[{level}] {msg}")


def list_serial_ports():
    """Verfügbare serielle Geräte sammeln."""
    return list(list_ports.comports())


def choose_serial_port(default_port=SERIAL_PORT):
    """Serielles Gerät interaktiv auswählen, wenn mehrere verfügbar sind."""
    configured_port = os.getenv('VISCA_SERIAL_PORT')
    if configured_port:
        return configured_port

    ports = list_serial_ports()

    if not ports:
        # No serial devices found: use default. This is common in CI
        # or headless containers where no /dev/ttyUSB* exists.
        log('W', 'Keine seriellen Geräte gefunden, verwende Standardport')
        return default_port

    print('\nVerfügbare serielle Geräte:')
    for index, port in enumerate(ports, start=1):
        description = port.description or 'unbekannt'
        manufacturer = f' | {port.manufacturer}' if port.manufacturer else ''
        print(f"  {index}) {port.device} - {description}{manufacturer}")

    # If not running in an interactive TTY (daemon/CI), don't attempt to
    # prompt the user; fall back to the default. Automated runs should set
    # VISCA_SERIAL_PORT to avoid surprises.
    if not sys.stdin.isatty():
        print(f"Kein interaktives Terminal, verwende Standardport: {default_port}")
        return default_port

    while True:
        try:
            choice = input(f"\nGerät wählen [1-{len(ports)}] oder Enter für {default_port}: ").strip()
            if choice == '':
                return default_port

            selected_index = int(choice) - 1
            if 0 <= selected_index < len(ports):
                return ports[selected_index].device

            print('Ungültige Auswahl.')
        except ValueError:
            print('Bitte eine Zahl eingeben.')


def setup_serial():
    """Open and configure the serial port.

    Returns True on success, False on failure. Uses choose_serial_port() to
    select the device and creates a pyserial Serial object assigned to the
    module-level `serial_conn` variable.
    """
    global serial_conn
    port_to_use = choose_serial_port()

    try:
        serial_conn = serial.Serial(
            port=port_to_use,
            baudrate=SERIAL_BAUDRATE,
            timeout=SERIAL_TIMEOUT,
            write_timeout=SERIAL_TIMEOUT,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE
        )
        # Buffer leeren
        serial_conn.reset_input_buffer()
        serial_conn.reset_output_buffer()
        log('I', f'Serial: {port_to_use}@{SERIAL_BAUDRATE}')
        return True
    except Exception as e:
        log('E', f'Serial Fehler: {e}')
        return False


def setup_visca_server():
    """Create, bind and listen on the VISCA TCP server socket.

    Returns True on success, False on failure. Binds to VISCA_IP_HOST:VISCA_IP_PORT.
    """
    global visca_socket
    try:
        visca_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        visca_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Try to set SO_REUSEPORT for quick restarts across processes. On
        # some platforms (older kernels, restricted containers) this may
        # raise; that's acceptable — the exception is caught below and
        # logged from the caller.
        try:
            visca_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except Exception:
            # Not fatal; continue without SO_REUSEPORT.
            pass
        visca_socket.setblocking(0)
        
        # Warte kurz falls Port noch im TIME_WAIT
        import time
        time.sleep(1)
        
        visca_socket.bind((VISCA_IP_HOST, VISCA_IP_PORT))
        visca_socket.listen(5)
        log('I', f'VISCA: {VISCA_IP_HOST}:{VISCA_IP_PORT}')
        return True
    except Exception as e:
        log('E', f'VISCA Fehler: {e}')
        log('E', f'Versuche Port mit: sudo lsof -i :{VISCA_IP_PORT}')
        return False


def read_serial_response(timeout=RESPONSE_WAIT):
    """Read a response from the serial device up to `timeout` seconds.

    VISCA messages are terminated with 0xFF. The loop reads available
    bytes and stops early when a trailing 0xFF is observed.
    """
    if not serial_conn or not serial_conn.is_open:
        return None
    
    start = time()
    response = b''
    
    while (time() - start) < timeout:
        try:
            if serial_conn.in_waiting > 0:
                chunk = serial_conn.read(serial_conn.in_waiting)
                response += chunk
                # VISCA response frames end with 0xFF; stop reading when
                # we see a chunk whose last byte is 0xFF.
                if chunk and chunk[-1] == 0xFF:
                    break
            sleep(0.01)
        except Exception as e:
            log('W', f'Serial read error: {e}')
            break
    
    return response if response else None


def handle_visca():
    """Accept new TCP clients and proxy data between TCP clients and serial.

    Called repeatedly from visca_loop(). Uses select() with a short timeout to
    avoid blocking the background thread.
    """
    global clients, stats
    # Build the readable list for select(): the listening socket plus any
    # currently connected client sockets. Sockets are non-blocking.
    readable = [visca_socket] + clients
    try:
        ready, _, _ = select.select(readable, [], [], 0.01)
    except Exception as e:
        log('W', f'Select error: {e}')
        return
    
    for sock in ready:
        if sock is visca_socket:
            # New connection on the listening socket
            try:
                client, addr = visca_socket.accept()
                client.setblocking(0)
                clients.append(client)
                stats['clients'] = len(clients)
                stats['total_conn'] += 1
                log('I', f'Client connected: {addr[0]}:{addr[1]}')
            except Exception as e:
                log('W', f'Accept error: {e}')
        else:
            # Data from a client socket
            try:
                data = sock.recv(1024)
                if data:
                    # An Serial weiterleiten
                    if serial_conn and serial_conn.is_open:
                        try:
                            serial_conn.write(data)
                            serial_conn.flush()
                            stats['ip_to_rs232'] += 1
                            stats['last_activity'] = int(time())
                            log('D', f'IP->RS232: {data.hex()}')
                            
                            # Wait for a (synchronous) response from the
                            # camera. Many VISCA commands produce an
                            # immediate response; read_serial_response will
                            # return None on timeout.
                            response = read_serial_response()
                            if response:
                                try:
                                    sock.send(response)
                                    stats['rs232_to_ip'] += 1
                                    log('D', f'RS232->IP: {response.hex()}')
                                except:
                                    pass
                        except Exception as e:
                            log('E', f'Serial write error: {e}')
                else:
                    # Client disconnected (recv returned empty bytes)
                    clients.remove(sock)
                    sock.close()
                    stats['clients'] = len(clients)
                    log('I', 'Client disconnected')
            except Exception as e:
                if sock in clients:
                    clients.remove(sock)
                    try:
                        sock.close()
                    except:
                        pass
                    stats['clients'] = len(clients)


def visca_loop():
    """Background loop that handles socket IO and unsolicited serial data.

    Runs in a daemon thread; relies on the global `running` flag for shutdown.
    """
    global running
    log('I', 'VISCA Loop gestartet')
    
    while running:
        try:
            handle_visca()
            
            # Unsolicited camera messages: if the camera sends bytes without
            # a preceding IP request, forward them to all connected clients.
            # This allows camera status messages to reach controllers.
            if serial_conn and serial_conn.is_open:
                try:
                    if serial_conn.in_waiting > 0:
                        data = serial_conn.read(serial_conn.in_waiting)
                        log('D', f'RS232 unsolicited: {data.hex()}')
                        for client in clients[:]:
                            try:
                                client.send(data)
                                stats['rs232_to_ip'] += 1
                            except:
                                clients.remove(client)
                                try:
                                    client.close()
                                except:
                                    pass
                except:
                    pass
            
            sleep(0.01)
        except Exception as e:
            log('E', f'VISCA loop error: {e}')
            sleep(0.1)


def send_command(hex_str):
    """Send a VISCA hex command over the serial link and wait for a response.

    Returns a dict with keys: ok (bool), len (bytes sent), resp (hex string or None)
    On error returns {'ok': False, 'err': '<message>'}.
    """
    try:
        # Hex String in Bytes konvertieren
        data = bytes.fromhex(hex_str.replace(' ', ''))
        
        if not serial_conn or not serial_conn.is_open:
            return {'ok': False, 'err': 'Serial port not ready'}
        
        # Senden
        serial_conn.write(data)
        serial_conn.flush()
        stats['ip_to_rs232'] += 1
        stats['last_activity'] = int(time())
        log('I', f'CMD sent: {hex_str}')
        
        # Auf Antwort warten
        response = read_serial_response()
        
        result = {
            'ok': True,
            'len': len(data),
            'resp': response.hex() if response else None
        }
        
        if response:
            log('I', f'CMD response: {response.hex()}')
        else:
            log('W', 'No response from camera')
        
        return result
        
    except Exception as e:
        log('E', f'CMD Error: {str(e)}')
        return {'ok': False, 'err': str(e)}



def main():
    """Entry point: open serial, start TCP server and run until SIGINT.

    The process exits early if the serial port or TCP server fail to start.
    For non-interactive environments set VISCA_SERIAL_PORT in the environment
    to avoid prompts.
    """
    global running
    
    print("=" * 40)
    print("VISCA Bridge - CV620 Edition (FIXED)")
    print("=" * 40)
    
    if not setup_serial():
        print("FEHLER: Serial Port kann nicht geöffnet werden")
        print(f"Prüfe: sudo chmod 666 {SERIAL_PORT}")
        return
    
    if not setup_visca_server():
        print("FEHLER: VISCA Server kann nicht gestartet werden")
        return
    
    # VISCA Thread starten
    visca_thread = Thread(target=visca_loop, daemon=True)
    visca_thread.start()
    
    try:
        while running:
            sleep(1)
    except KeyboardInterrupt:
        print("\nShutdown...")
        running = False
        if serial_conn:
            serial_conn.close()
        if visca_socket:
            visca_socket.close()
        for client in clients:
            try:
                client.close()
            except:
                pass


if __name__ == "__main__":
    main()
