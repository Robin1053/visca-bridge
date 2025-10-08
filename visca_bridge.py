#!/usr/bin/env python3
"""
VISCA Bridge - Optimiert für Raspberry Pi Zero mit CV620 Presets
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
from urllib.parse import urlparse


HTML_CACHE = None


# Konfiguration
VISCA_IP_HOST = '0.0.0.0'
VISCA_IP_PORT = 52381
WEB_PORT = 8080
SERIAL_PORT = '/dev/serial0'
SERIAL_BAUDRATE = 9600
MAX_LOG_ENTRIES = 50

# VISCA Command Presets für CV620
VISCA_PRESETS = {
    # Power
    'power_on': '81 01 04 00 02 FF',
    'power_off': '81 01 04 00 03 FF',
    'power_query': '81 09 04 00 FF',
    
    # Zoom
    'zoom_stop': '81 01 04 07 00 FF',
    'zoom_tele': '81 01 04 07 02 FF',
    'zoom_wide': '81 01 04 07 03 FF',
    'zoom_tele_fast': '81 01 04 07 27 FF',
    'zoom_wide_fast': '81 01 04 07 37 FF',
    
    # Focus
    'focus_stop': '81 01 04 08 00 FF',
    'focus_far': '81 01 04 08 02 FF',
    'focus_near': '81 01 04 08 03 FF',
    'focus_auto': '81 01 04 38 02 FF',
    'focus_manual': '81 01 04 38 03 FF',
    'focus_onepush': '81 01 04 18 01 FF',
    
    # White Balance
    'wb_auto': '81 01 04 35 00 FF',
    'wb_indoor': '81 01 04 35 01 FF',
    'wb_outdoor': '81 01 04 35 02 FF',
    'wb_onepush': '81 01 04 35 03 FF',
    'wb_manual': '81 01 04 35 05 FF',
    
    # Exposure
    'ae_full_auto': '81 01 04 39 00 FF',
    'ae_manual': '81 01 04 39 03 FF',
    'ae_shutter_priority': '81 01 04 39 0A FF',
    'ae_iris_priority': '81 01 04 39 0B FF',
    
    # Pan/Tilt
    'pt_home': '81 01 06 04 FF',
    'pt_reset': '81 01 06 05 FF',
    'pt_stop': '81 01 06 01 18 18 03 03 FF',
    'pt_up': '81 01 06 01 0C 0C 03 01 FF',
    'pt_down': '81 01 06 01 0C 0C 03 02 FF',
    'pt_left': '81 01 06 01 0C 0C 01 03 FF',
    'pt_right': '81 01 06 01 0C 0C 02 03 FF',
    
    # Memory/Preset
    'preset_recall_0': '81 01 04 3F 02 00 FF',
    'preset_recall_1': '81 01 04 3F 02 01 FF',
    'preset_recall_2': '81 01 04 3F 02 02 FF',
    'preset_recall_3': '81 01 04 3F 02 03 FF',
    'preset_set_0': '81 01 04 3F 01 00 FF',
    'preset_set_1': '81 01 04 3F 01 01 FF',
    'preset_set_2': '81 01 04 3F 01 02 FF',
    'preset_set_3': '81 01 04 3F 01 03 FF',
    
    # Picture
    'backlight_on': '81 01 04 33 02 FF',
    'backlight_off': '81 01 04 33 03 FF',
    'mirror_on': '81 01 04 61 02 FF',
    'mirror_off': '81 01 04 61 03 FF',
    'flip_on': '81 01 04 66 02 FF',
    'flip_off': '81 01 04 66 03 FF',
    
    # System
    'menu_on': '81 01 06 06 02 FF',
    'menu_off': '81 01 06 06 03 FF',
    'if_clear': '88 01 00 01 FF',
}

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
    """Minimales Logging"""
    with log_lock:
        entry = {'t': int(time()), 'l': level[0], 'm': msg}
        log_queue.appendleft(entry)
        print(f"[{level}] {msg}")


def setup_serial():
    """Serial Port öffnen"""
    global serial_conn
    try:
        serial_conn = serial.Serial(
            port=SERIAL_PORT,
            baudrate=SERIAL_BAUDRATE,
            timeout=0.1,
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
        visca_socket.setblocking(0)
        visca_socket.bind((VISCA_IP_HOST, VISCA_IP_PORT))
        visca_socket.listen(3)
        log('I', f'VISCA: {VISCA_IP_HOST}:{VISCA_IP_PORT}')
        return True
    except Exception as e:
        log('E', f'VISCA Fehler: {e}')
        return False


def handle_visca():
    """VISCA Verbindungen verarbeiten"""
    global clients, stats
    
    readable = [visca_socket] + clients
    try:
        ready, _, _ = select.select(readable, [], [], 0.01)
    except:
        return
    
    for sock in ready:
        if sock is visca_socket:
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
            try:
                data = sock.recv(1024)
                if data:
                    if serial_conn and serial_conn.is_open:
                        serial_conn.write(data)
                        stats['ip_to_rs232'] += 1
                        stats['last_activity'] = int(time())
                        
                        sleep(0.05)
                        if serial_conn.in_waiting > 0:
                            resp = serial_conn.read(serial_conn.in_waiting)
                            sock.send(resp)
                            stats['rs232_to_ip'] += 1
                else:
                    clients.remove(sock)
                    sock.close()
                    stats['clients'] = len(clients)
            except:
                if sock in clients:
                    clients.remove(sock)
                    sock.close()
                    stats['clients'] = len(clients)


def visca_loop():
    """VISCA Haupt-Loop"""
    global running
    log('I', 'VISCA Loop gestartet')
    
    while running:
        handle_visca()
        
        if serial_conn and serial_conn.is_open:
            try:
                if serial_conn.in_waiting > 0:
                    data = serial_conn.read(serial_conn.in_waiting)
                    for client in clients[:]:
                        try:
                            client.send(data)
                        except:
                            clients.remove(client)
                            client.close()
            except:
                pass
        
        sleep(0.01)


def send_command(hex_str):
    """VISCA Befehl senden"""
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
            
            log('I', f'CMD: {hex_str[:30]}...')
            return {'ok': True, 'resp': resp}
        return {'ok': False, 'err': 'Serial nicht bereit'}
    except Exception as e:
        log('E', f'CMD Error: {str(e)}')
        return {'ok': False, 'err': str(e)}


class WebHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass
    
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
                'log': list(log_queue)[:20]
            }
            self.wfile.write(json.dumps(data).encode())
        elif path == '/api/presets':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(VISCA_PRESETS).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/cmd':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            result = send_command(data.get('hex', ''))
            
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
            path = os.path.join(os.path.dirname(__file__), 'web', 'index.html')
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
    print("VISCA Bridge - CV620 Edition")
    print("=" * 40)
    
    if not setup_serial():
        print("FEHLER: Serial Port")
        return
    
    if not setup_visca_server():
        print("FEHLER: VISCA Server")
        return
    
    visca_thread = Thread(target=visca_loop, daemon=True)
    visca_thread.start()
    
    try:
        run_web()
    except KeyboardInterrupt:
        print("\nShutdown...")
        running = False
        if serial_conn:
            serial_conn.close()
        if visca_socket:
            visca_socket.close()
        for client in clients:
            client.close()


if __name__ == "__main__":
    main()