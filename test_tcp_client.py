#!/usr/bin/env python3
"""
Test-Client für VISCA TCP Server
Testet die Verbindung und sendet einige VISCA-Befehle
"""

import socket
import sys
from time import sleep


def connect_tcp(host='localhost', port=52381):
    """Verbindung zum TCP Server herstellen"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        print(f"✓ Verbunden mit {host}:{port}")
        return sock
    except Exception as e:
        print(f"✗ Verbindungsfehler: {e}")
        return None


def send_command(sock, hex_command, description=""):
    """VISCA Befehl senden und Antwort empfangen"""
    try:
        # Hex-String in Bytes konvertieren
        data = bytes.fromhex(hex_command.replace(' ', ''))
        
        print(f"\n→ Sende: {hex_command} {description}")
        sock.send(data)
        
        # Antwort empfangen (mit Timeout)
        sock.settimeout(1.0)
        try:
            response = sock.recv(1024)
            if response:
                print(f"← Antwort: {response.hex()}")
                return response
            else:
                print("← Keine Antwort")
                return None
        except socket.timeout:
            print("← Timeout (keine Antwort)")
            return None
            
    except Exception as e:
        print(f"✗ Fehler: {e}")
        return None


def main():
    """Haupt-Testfunktion"""
    
    # Parameter
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 52381
    
    print("=" * 60)
    print("VISCA TCP Test Client")
    print("=" * 60)
    
    # Verbinden
    sock = connect_tcp(host, port)
    if not sock:
        return 1
    
    try:
        # Test-Befehle
        print("\n" + "=" * 60)
        print("Teste VISCA Befehle...")
        print("=" * 60)
        
        # 1. Address Set (optional, normalerweise nicht nötig)
        send_command(sock, "88 30 01 FF", "(Address Set - Broadcast)")
        sleep(0.5)
        
        # 2. IF_Clear (Buffer leeren)
        send_command(sock, "81 01 00 01 FF", "(IF_Clear - Command Buffer leeren)")
        sleep(0.5)
        
        # 3. Power Query
        send_command(sock, "81 09 04 00 FF", "(Power Inquiry)")
        sleep(0.5)
        
        # 4. Zoom Query
        send_command(sock, "81 09 04 47 FF", "(Zoom Position Inquiry)")
        sleep(0.5)
        
        # 5. Pan/Tilt Query
        send_command(sock, "81 09 06 12 FF", "(Pan/Tilt Position Inquiry)")
        sleep(0.5)
        
        print("\n" + "=" * 60)
        print("Test abgeschlossen")
        print("=" * 60)
        
        # Optional: Interaktiver Modus
        print("\nInteraktiver Modus (Ctrl+C zum Beenden)")
        print("Gib VISCA Hex-Befehle ein (z.B. '8101040002FF'):")
        
        while True:
            try:
                cmd = input("\n> ").strip()
                if cmd:
                    send_command(sock, cmd, "(Custom Command)")
            except KeyboardInterrupt:
                print("\n\nBeende...")
                break
        
    finally:
        sock.close()
        print("Verbindung geschlossen")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
