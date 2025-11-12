#!/usr/bin/env python3
"""
VISCA Bridge - Optimiert für Raspberry Pi Zero mit CV620 Presets
FIXED VERSION - Timeout und Fehlerbehandlung verbessert
"""

import socket
import serial
import select
import json
from time import time, sleep
from collections import deque
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread, Lock
from urllib.parse import urlparse


# Konfiguration
VISCA_IP_HOST = '0.0.0.0'
VISCA_IP_PORT = 1259  # Ändere zu 52382 falls Port belegt
WEB_PORT = 8081
SERIAL_PORT = '/dev/ttyUSB0'
SERIAL_BAUDRATE = 9600
SERIAL_TIMEOUT = 1.0  # Erhöht von 0.1 auf 1.0 Sekunde
MAX_LOG_ENTRIES = 100
RESPONSE_WAIT = 0.3  # Zeit auf Kamera-Antwort warten

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
    'preset_recall_4': '81 01 04 3F 02 04 FF',
    'preset_recall_5': '81 01 04 3F 02 05 FF',
    'preset_recall_6': '81 01 04 3F 02 06 FF',
    'preset_recall_7': '81 01 04 3F 02 07 FF',
    'preset_recall_8': '81 01 04 3F 02 08 FF',
    'preset_recall_9': '81 01 04 3F 02 09 FF',
    'preset_set_0': '81 01 04 3F 01 00 FF',
    'preset_set_1': '81 01 04 3F 01 01 FF',
    'preset_set_2': '81 01 04 3F 01 02 FF',
    'preset_set_3': '81 01 04 3F 01 03 FF',
    'preset_set_4': '81 01 04 3F 01 04 FF',
    'preset_set_5': '81 01 04 3F 01 05 FF',
    'preset_set_6': '81 01 04 3F 01 06 FF',
    'preset_set_7': '81 01 04 3F 01 07 FF',
    'preset_set_8': '81 01 04 3F 01 08 FF',
    'preset_set_9': '81 01 04 3F 01 09 FF',
    
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
    """Logging mit Thread-Safety"""
    with log_lock:
        entry = {'t': int(time()), 'l': level[0], 'm': msg}
        log_queue.appendleft(entry)
        timestamp = time()
        print(f"[{level}] {msg}")


def setup_serial():
    """Serial Port öffnen mit verbesserter Fehlerbehandlung"""
    global serial_conn
    try:
        serial_conn = serial.Serial(
            port=SERIAL_PORT,
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


class WebHandler(BaseHTTPRequestHandler):
    """Web Server Handler mit CORS Support"""
    
    def log_message(self, *args):
        """Disable default logging"""
        pass
    
    def end_headers(self):
        """CORS Headers hinzufügen"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        BaseHTTPRequestHandler.end_headers(self)
    
    def do_OPTIONS(self):
        """CORS Preflight"""
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        """GET Requests"""
        path = urlparse(self.path).path
        
        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = b'''
            <html>
            <head><title>VISCA Bridge</title></head>
            <body>
                <h1>VISCA Bridge Running</h1>
                <p>Use React Frontend or API:</p>
                <ul>
                    <li>GET /api/stats - Status</li>
                    <li>GET /api/presets - Commands</li>
                    <li>POST /api/cmd - Send command</li>
                </ul>
            </body>
            </html>
            '''
            self.wfile.write(html)
            
        elif path == '/api/stats':
            try:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                with log_lock:
                    log_list = [dict(entry) for entry in list(log_queue)[:50]]
                
                data = {
                    'run': bool(running),
                    'ser': bool(serial_conn and serial_conn.is_open),
                    'cli': int(stats['clients']),
                    'tot': int(stats['total_conn']),
                    'i2r': int(stats['ip_to_rs232']),
                    'r2i': int(stats['rs232_to_ip']),
                    'act': int(stats['last_activity']),
                    'start': int(stats['start_time']),
                    'port': str(SERIAL_PORT),
                    'baud': int(SERIAL_BAUDRATE),
                    'vport': int(VISCA_IP_PORT),
                    'log': log_list
                }
                
                json_str = json.dumps(data, ensure_ascii=False)
                self.wfile.write(json_str.encode('utf-8'))
            except Exception as e:
                log('E', f'Stats API error: {e}')
                self.send_error(500, str(e))
            
        elif path == '/api/presets':
            try:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                json_str = json.dumps(VISCA_PRESETS, ensure_ascii=False)
                self.wfile.write(json_str.encode('utf-8'))
            except Exception as e:
                log('E', f'Presets API error: {e}')
                self.send_error(500, str(e))
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """POST Requests"""
        if self.path == '/api/cmd':
            try:
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length)
                data = json.loads(body)
                
                hex_command = data.get('hex', '')
                if not hex_command:
                    result = {'ok': False, 'err': 'No hex command provided'}
                else:
                    result = send_command(hex_command)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error = {'ok': False, 'err': str(e)}
                self.wfile.write(json.dumps(error).encode())
        else:
            self.send_response(404)
            self.end_headers()


def run_web():
    """Web Server starten"""
    server = HTTPServer(('0.0.0.0', WEB_PORT), WebHandler)
    log('I', f'Web: http://0.0.0.0:{WEB_PORT}')
    server.serve_forever()


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
        run_web()
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