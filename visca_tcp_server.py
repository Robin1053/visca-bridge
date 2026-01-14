"""
VISCA TCP Server
Handles multiple TCP client connections and forwards VISCA commands to serial transport.
"""

import socket
import select
import threading
import logging
from time import time, sleep

log = logging.getLogger("visca-tcp")


class ViscaTCPServer(threading.Thread):
    def __init__(self, transport, host='0.0.0.0', port=1259, response_wait=0.3):
        super().__init__(daemon=True)
        self.transport = transport
        self.host = host
        self.port = port
        self.response_wait = response_wait
        self.running = True
        self.clients = []
        self.stats = {
            'clients': 0,
            'total_conn': 0,
            'ip_to_rs232': 0,
            'rs232_to_ip': 0,
            'last_activity': 0
        }
        
        # TCP Socket erstellen
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Platform-specific: SO_REUSEPORT nur auf Unix-Systemen
        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
            pass  # Windows unterstützt SO_REUSEPORT nicht
        
        self.socket.setblocking(0)
        
        # Bind mit Retry-Logik
        max_retries = 3
        for attempt in range(max_retries):
            try:
                sleep(1)  # Kurz warten, falls Port noch im TIME_WAIT
                self.socket.bind((self.host, self.port))
                break
            except OSError as e:
                if attempt < max_retries - 1:
                    log.warning(f"[TCP] Bind retry {attempt + 1}/{max_retries}: {e}")
                    sleep(2)
                else:
                    raise
        
        self.socket.listen(5)
        log.info(f"[TCP] VISCA TCP listening on {self.host}:{self.port}")
    
    def run(self):
        """Haupt-Loop für TCP Server"""
        log.info("[TCP] Server thread started")
        
        while self.running:
            try:
                self._handle_connections()
                self._handle_unsolicited_messages()
                sleep(0.01)
            except Exception as e:
                log.error(f"[TCP] Loop error: {e}")
                sleep(0.1)
    
    def _handle_connections(self):
        """Neue Verbindungen und Client-Daten verarbeiten"""
        readable = [self.socket] + self.clients
        
        try:
            ready, _, _ = select.select(readable, [], [], 0.01)
        except Exception as e:
            log.warning(f"[TCP] Select error: {e}")
            return
        
        for sock in ready:
            if sock is self.socket:
                # Neue Verbindung akzeptieren
                try:
                    client, addr = self.socket.accept()
                    client.setblocking(0)
                    self.clients.append(client)
                    self.stats['clients'] = len(self.clients)
                    self.stats['total_conn'] += 1
                    log.info(f"[TCP] Client connected: {addr[0]}:{addr[1]}")
                except Exception as e:
                    log.warning(f"[TCP] Accept error: {e}")
            else:
                # Daten von Client empfangen
                self._handle_client_data(sock)
    
    def _handle_client_data(self, client_sock):
        """Daten von einem Client verarbeiten"""
        try:
            data = client_sock.recv(1024)
            
            if not data:
                # Client hat Verbindung geschlossen
                self._remove_client(client_sock)
                return
            
            # An Serial weiterleiten
            log.debug(f"[TCP] IP->RS232: {data.hex()}")
            self.transport.send(data)
            self.stats['ip_to_rs232'] += 1
            self.stats['last_activity'] = int(time())
            
            # Auf Antwort von Kamera warten
            response = self._read_serial_response()
            if response:
                try:
                    client_sock.send(response)
                    self.stats['rs232_to_ip'] += 1
                    log.debug(f"[TCP] RS232->IP: {response.hex()}")
                except Exception as e:
                    log.warning(f"[TCP] Send response error: {e}")
            
        except BlockingIOError:
            # Keine Daten verfügbar (non-blocking socket)
            pass
        except Exception as e:
            log.warning(f"[TCP] Client data error: {e}")
            self._remove_client(client_sock)
    
    def _read_serial_response(self):
        """
        Liest Antwort von Serial Port mit Timeout
        VISCA Antworten enden immer mit 0xFF
        """
        start = time()
        response = b''
        
        while (time() - start) < self.response_wait:
            try:
                # Prüfen ob Daten verfügbar (non-blocking check)
                if hasattr(self.transport.serial, 'in_waiting') and self.transport.serial.in_waiting > 0:
                    chunk = self.transport.serial.read(self.transport.serial.in_waiting)
                    response += chunk
                    
                    # VISCA Antwort endet mit 0xFF
                    if chunk and chunk[-1] == 0xFF:
                        break
                
                sleep(0.01)
            except Exception as e:
                log.warning(f"[TCP] Serial read error: {e}")
                break
        
        return response if response else None
    
    def _handle_unsolicited_messages(self):
        """
        Unaufgeforderte Nachrichten von Kamera an alle Clients verteilen
        (z.B. Status-Updates, Bewegungs-Completion, etc.)
        """
        try:
            if hasattr(self.transport.serial, 'in_waiting') and self.transport.serial.in_waiting > 0:
                data = self.transport.serial.read(self.transport.serial.in_waiting)
                if data:
                    log.debug(f"[TCP] RS232 unsolicited: {data.hex()}")
                    
                    # An alle Clients senden
                    for client in self.clients[:]:  # Copy der Liste für sichere Iteration
                        try:
                            client.send(data)
                            self.stats['rs232_to_ip'] += 1
                        except Exception as e:
                            log.warning(f"[TCP] Broadcast error: {e}")
                            self._remove_client(client)
        except Exception as e:
            log.debug(f"[TCP] Unsolicited check error: {e}")
    
    def _remove_client(self, client_sock):
        """Client-Verbindung sauber entfernen"""
        if client_sock in self.clients:
            self.clients.remove(client_sock)
            self.stats['clients'] = len(self.clients)
            log.info("[TCP] Client disconnected")
        
        try:
            client_sock.close()
        except:
            pass
    
    def get_stats(self):
        """Statistiken abrufen"""
        return self.stats.copy()
    
    def stop(self):
        """Server beenden"""
        log.info("[TCP] Stopping server...")
        self.running = False
        
        # Alle Clients schließen
        for client in self.clients[:]:
            try:
                client.close()
            except:
                pass
        
        self.clients.clear()
        
        # Server-Socket schließen
        try:
            self.socket.close()
        except:
            pass
        
        log.info("[TCP] Server stopped")
