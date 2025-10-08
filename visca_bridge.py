#!/usr/bin/env python3
"""
VISCA Bridge - Optimiert für Raspberry Pi Zero
Ultra-leichtgewichtig mit minimalem Ressourcen-Verbrauch
"""


import os
import socket
import serial
import select
import sys
import json
from time import time, sleep
from collections import deque
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread, Lock
from urllib.parse import urlparse, parse_qs

# Konfiguration
VISCA_IP_HOST = '0.0.0.0'
VISCA_IP_PORT = 52381
WEB_PORT = 8080
SERIAL_PORT = '/dev/serial0'
SERIAL_BAUDRATE = 9600
MAX_LOG_ENTRIES = 50  # Begrenzt für RAM

# Globale Variablen (effizienter als Klassen auf Pi Zero)
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
    """Minimales Logging"""
    with log_lock:
        entry = {
            't': int(time()),
            'l': level[0],  # Nur erster Buchstabe
            'm': msg
        }
        log_queue.appendleft(entry)
        print(f"[{level}] {msg}")


def setup_serial():
    """Serial Port öffnen"""
    global serial_conn
    try:
        serial_conn = serial.Serial(
            port=SERIAL_PORT,
            baudrate=SERIAL_BAUDRATE,
            timeout=0.1,  # Non-blocking
            write_timeout=0.1
        )
        log('I', f'Serial: {SERIAL_PORT}@{SERIAL_BAUDRATE}')
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
        visca_socket.setblocking(0)  # Non-blocking
        visca_socket.bind((VISCA_IP_HOST, VISCA_IP_PORT))
        visca_socket.listen(3)
        log('I', f'VISCA: {VISCA_IP_HOST}:{VISCA_IP_PORT}')
        return True
    except Exception as e:
        log('E', f'VISCA Fehler: {e}')
        return False


def handle_visca():
    """VISCA Verbindungen verarbeiten (non-blocking)"""
    global clients, stats, running
    
    # Neue Verbindungen akzeptieren
    readable = [visca_socket] + clients
    try:
        ready, _, _ = select.select(readable, [], [], 0.01)
    except:
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
                log('I', f'Client: {addr[0]}')
            except:
                pass
        else:
            # Daten von Client
            try:
                data = sock.recv(1024)
                if data:
                    # An RS232 senden
                    if serial_conn and serial_conn.is_open:
                        serial_conn.write(data)
                        stats['ip_to_rs232'] += 1
                        stats['last_activity'] = int(time())
                        
                        # Auf Antwort warten (kurz)
                        sleep(0.05)
                        if serial_conn.in_waiting > 0:
                            resp = serial_conn.read(serial_conn.in_waiting)
                            sock.send(resp)
                            stats['rs232_to_ip'] += 1
                else:
                    # Verbindung geschlossen
                    clients.remove(sock)
                    sock.close()
                    stats['clients'] = len(clients)
            except:
                # Fehler -> Client entfernen
                if sock in clients:
                    clients.remove(sock)
                    sock.close()
                    stats['clients'] = len(clients)


def visca_loop():
    """Haupt-Loop für VISCA (läuft in Thread)"""
    global running
    log('I', 'VISCA Loop gestartet')
    
    while running:
        handle_visca()
        
        # RS232 -> IP forwarding
        if serial_conn and serial_conn.is_open:
            try:
                if serial_conn.in_waiting > 0:
                    data = serial_conn.read(serial_conn.in_waiting)
                    # An alle Clients senden
                    for client in clients[:]:
                        try:
                            client.send(data)
                        except:
                            clients.remove(client)
                            client.close()
            except:
                pass
        
        sleep(0.01)  # CPU schonen


def send_manual_cmd(hex_str):
    """Manueller Befehl"""
    try:
        data = bytes.fromhex(hex_str.replace(' ', ''))
        if serial_conn and serial_conn.is_open:
            serial_conn.write(data)
            stats['ip_to_rs232'] += 1
            stats['last_activity'] = int(time())
            
            sleep(0.1)
            resp = None
            if serial_conn.in_waiting > 0:
                resp = serial_conn.read(serial_conn.in_waiting).hex()
            
            log('I', f'CMD: {hex_str}')
            return {'ok': True, 'resp': resp}
        return {'ok': False, 'err': 'Serial nicht bereit'}
    except Exception as e:
        return {'ok': False, 'err': str(e)}


# Web-Handler (minimal)
class WebHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # Keine HTTP Logs
    
    def do_GET(self):
        path = urlparse(self.path).path
        
        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(get_html())
        elif path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Stats zusammenstellen
            data = {
                'run': running,
                'ser': serial_conn.is_open if serial_conn else False,
                'cli': stats['clients'],
                'tot': stats['total_conn'],
                'i2r': stats['ip_to_rs232'],
                'r2i': stats['rs232_to_ip'],
                'act': stats['last_activity'],
                'start': stats['start_time'],
                'port': SERIAL_PORT,
                'baud': SERIAL_BAUDRATE,
                'vport': VISCA_IP_PORT,
                'log': list(log_queue)[:20]  # Nur letzte 20
            }
            self.wfile.write(json.dumps(data).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/cmd':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            result = send_manual_cmd(data.get('hex', ''))
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_response(404)
            self.end_headers()


def get_html():
    global HTML_CACHE
    if HTML_CACHE is None:
        try:
            path = os.path.join(os.path.dirname(__file__),'index.html')
            with open(path, 'r', encoding='utf-8') as f:
                HTML_CACHE = f.read()
        except Exception as e:
            log('E', f'HTML konnte nicht geladen werden: {e}')
            HTML_CACHE = "<h1>Fehler beim Laden des Web-UI</h1>"
    return HTML_CACHE


def run_web():
    """Web Server starten"""
    server = HTTPServer(('0.0.0.0', WEB_PORT), WebHandler)
    log('I', f'Web: http://0.0.0.0:{WEB_PORT}')
    server.serve_forever()


def main():
    """Hauptfunktion"""
    global running
    
    print("=" * 40)
    print("VISCA Bridge - Pi Zero Optimiert")
    print("=" * 40)
    
    # Serial Setup
    if not setup_serial():
        print("FEHLER: Serial Port konnte nicht geöffnet werden")
        return
    
    # VISCA Server Setup
    if not setup_visca_server():
        print("FEHLER: VISCA Server konnte nicht gestartet werden")
        return
    
    # VISCA Thread starten
    visca_thread = Thread(target=visca_loop, daemon=True)
    visca_thread.start()
    
    # Web Server starten (blocking)
    try:
        run_web()
    except KeyboardInterrupt:
        print("\nShutdown...")
        running = False
        
        # Cleanup
        if serial_conn:
            serial_conn.close()
        if visca_socket:
            visca_socket.close()
        for client in clients:
            client.close()


if __name__ == "__main__":
    main()