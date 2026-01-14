# VISCA TCP Integration - Änderungsübersicht

## Neue Dateien

### 1. `visca_tcp_server.py`
Vollständige TCP-Server-Implementierung mit folgenden Features:
- Multi-Client Support (mehrere gleichzeitige Verbindungen)
- Bidirektionale Kommunikation (Client ↔ Serial)
- Automatisches Response-Handling
- Unsolicited Message Broadcasting an alle Clients
- Thread-safe Client-Verwaltung
- Detaillierte Statistiken

### 2. `VISCA_TCP_README.md`
Ausführliche Dokumentation für:
- Verwendung des TCP-Servers
- Konfigurationsoptionen
- Client-Beispiele (Python, netcat)
- VISCA-Protokoll-Grundlagen
- Troubleshooting

### 3. `test_tcp_client.py`
Test-Client zum Testen der TCP-Funktionalität:
- Verbindungstest
- Vordefinierte VISCA-Befehle
- Interaktiver Modus für manuelle Tests

## Geänderte Dateien

### `main.py`
**Änderungen:**
1. Import von `ViscaTCPServer` hinzugefügt
2. Separate Ports für UDP und TCP definiert:
   - `VISCA_UDP_PORT = 1259` (für Sony VISCA-over-UDP)
   - `VISCA_TCP_PORT = 52381` (für Standard VISCA-over-TCP)
3. TCP-Server initialisiert und gestartet
4. Neue API-Endpoints:
   - `GET /api/stats` - Gibt Statistiken über TCP/UDP/Serial zurück
   - `GET /` - Status-Seite mit Konfigurationsübersicht

## Verwendung

### Server starten

```bash
python main.py
```

Der Server startet nun **beide** Protokolle:
- **UDP** auf Port 1259 (für Sony VISCA-over-UDP mit Header)
- **TCP** auf Port 52381 (für Standard VISCA-over-TCP)
- **HTTP** auf Port 8081 (Web-API)

### Mit TCP-Server verbinden

**Python Client:**
```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 52381))
sock.send(bytes.fromhex('8101040002FF'))  # Power ON
response = sock.recv(1024)
print(response.hex())
sock.close()
```

**Test-Client verwenden:**
```bash
python test_tcp_client.py localhost 52381
```

**Mit netcat testen:**
```bash
echo "8101040002FF" | xxd -r -p | nc localhost 52381 | xxd -p
```

### Statistiken abrufen

```bash
curl http://localhost:8081/api/stats
```

**Response:**
```json
{
  "tcp": {
    "host": "0.0.0.0",
    "port": 52381,
    "clients": 2,
    "total_connections": 5,
    "ip_to_rs232": 42,
    "rs232_to_ip": 42,
    "last_activity": 1705248000
  },
  "udp": {
    "port": 1259
  },
  "serial": {
    "port": "/dev/ttyUSB0",
    "baudrate": 9600,
    "connected": true
  }
}
```

## Konfiguration

In `main.py` können folgende Parameter angepasst werden:

```python
VISCA_IP_HOST = '0.0.0.0'      # Bind-Adresse
VISCA_UDP_PORT = 1259           # UDP Port (Sony Format)
VISCA_TCP_PORT = 52381          # TCP Port (Standard VISCA)
WEB_PORT = 8081                 # HTTP API Port
SERIAL_PORT = '/dev/ttyUSB0'   # Serial Port
SERIAL_BAUDRATE = 9600          # Baudrate
RESPONSE_WAIT = 0.3             # Warte-Zeit auf Kamera-Antwort (Sekunden)
```

## Technische Details

### TCP vs UDP

| Feature | TCP | UDP |
|---------|-----|-----|
| Verbindung | Verbindungsorientiert | Verbindungslos |
| Zuverlässigkeit | Garantierte Zustellung | Keine Garantie |
| Response-Handling | Automatisch | Manuell |
| Multi-Client | Ja (Sessions) | Nein |
| Sony Header | Nein | Ja (optional) |

### VISCA-Protokoll

Alle VISCA-Befehle enden mit `0xFF`:
- Byte 1: Adresse (z.B. `0x81` für Kamera 1)
- Bytes 2-N: Befehl
- Letztes Byte: `0xFF` (Terminator)

Beispiele:
```
8101040002FF  - Power ON
8101040003FF  - Power OFF
8101060112FF  - Zoom Tele
8101060113FF  - Zoom Wide
8109040000FF  - Power Inquiry
```

### Thread-Architektur

```
main.py (Flask)
    ├── SerialViscaTransport (Thread)
    ├── ViscaUDPServer (Thread)
    └── ViscaTCPServer (Thread)
            ├── Connection Handler
            ├── Response Handler
            └── Broadcast Handler
```

## Troubleshooting

### Port bereits belegt

**Windows:**
```powershell
netstat -an | findstr 52381
```

**Linux/macOS:**
```bash
lsof -i :52381
```

**Lösung:** Ändere `VISCA_TCP_PORT` in `main.py` zu einem freien Port.

### SO_REUSEPORT Fehler unter Windows

Wird automatisch behandelt - `SO_REUSEPORT` wird nur auf Unix-Systemen verwendet.

### Keine Antwort von Kamera

1. Serial-Verbindung prüfen
2. `RESPONSE_WAIT` erhöhen (z.B. auf 0.5 oder 1.0)
3. Baudrate prüfen (Standard: 9600)

## Logging

Detaillierte Logs aktivieren:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Kompatibilität

- **Windows**: ✅ Vollständig unterstützt
- **Linux**: ✅ Vollständig unterstützt (inkl. Raspberry Pi)
- **macOS**: ✅ Vollständig unterstützt

## Nächste Schritte

Optional können weitere Features hinzugefügt werden:
- [ ] WebSocket-Support für Echtzeit-Updates im Frontend
- [ ] TLS/SSL-Verschlüsselung für TCP
- [ ] Authentifizierung für TCP-Clients
- [ ] Load Balancing für mehrere Kameras
- [ ] VISCA-Befehlsvalidierung vor Weiterleitung
