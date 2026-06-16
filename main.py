#!/usr/bin/env python3
"""
VISCA Bridge - Optimiert für Raspberry Pi Zero mit CV620 Presets
FIXED VERSION - Timeout und Fehlerbehandlung verbessert
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
    """Einfache .env-Datei aus dem Projektverzeichnis laden."""
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
        log('W', 'Keine seriellen Geräte gefunden, verwende Standardport')
        return default_port

    print('\nVerfügbare serielle Geräte:')
    for index, port in enumerate(ports, start=1):
        description = port.description or 'unbekannt'
        manufacturer = f' | {port.manufacturer}' if port.manufacturer else ''
        print(f"  {index}) {port.device} - {description}{manufacturer}")

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
    """Serial Port öffnen mit verbesserter Fehlerbehandlung"""
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
    """VISCA TCP Server"""
    global visca_socket
    try:
        visca_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        visca_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        visca_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
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
    """Serial Antwort mit Timeout lesen"""
    if not serial_conn or not serial_conn.is_open:
        return None
    
    start = time()
    response = b''
    
    while (time() - start) < timeout:
        try:
            if serial_conn.in_waiting > 0:
                chunk = serial_conn.read(serial_conn.in_waiting)
                response += chunk
                # VISCA Antwort endet immer mit FF
                if chunk and chunk[-1] == 0xFF:
                    break
            sleep(0.01)
        except Exception as e:
            log('W', f'Serial read error: {e}')
            break
    
    return response if response else None


def handle_visca():
    """VISCA Verbindungen verarbeiten"""
    global clients, stats
    
    readable = [visca_socket] + clients
    try:
        ready, _, _ = select.select(readable, [], [], 0.01)
    except Exception as e:
        log('W', f'Select error: {e}')
        return
    
    for sock in ready:
        if sock is visca_socket:
            # Neue Verbindung
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
            # Daten von Client
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
                            
                            # Auf Antwort warten
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
                    # Client disconnected
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
    """VISCA Haupt-Loop"""
    global running
    log('I', 'VISCA Loop gestartet')
    
    while running:
        try:
            handle_visca()
            
            # Unaufgeforderte Kamera-Nachrichten an alle Clients
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
    """VISCA Befehl senden mit verbesserter Fehlerbehandlung"""
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
    """Hauptfunktion"""
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