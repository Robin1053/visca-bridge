bitte jetzt noch die Re# VISCA TCP Server

Diese Datei implementiert einen VISCA TCP Server, der mehrere gleichzeitige Client-Verbindungen unterstützt.

## Features

- **Multi-Client Support**: Mehrere VISCA-Controller können gleichzeitig verbunden werden
- **Bidirektionale Kommunikation**: 
  - Client → Serial: VISCA-Befehle werden an die Kamera weitergeleitet
  - Serial → Client: Antworten und unaufgeforderte Nachrichten werden zurückgesendet
- **Automatisches Response-Handling**: Wartet auf Kamera-Antworten und sendet diese zurück
- **Thread-safe**: Sichere Verwaltung mehrerer Clients
- **Statistiken**: Tracking von Verbindungen und übertragenen Nachrichten

## Verwendung

### Start über main.py

Der TCP-Server wird automatisch beim Start von `main.py` gestartet:

```python
from visca_tcp_server import ViscaTCPServer

tcp_server = ViscaTCPServer(
    transport=transport,
    host='0.0.0.0',
    port=52381,
    response_wait=0.3
)
tcp_server.start()
```

### Konfiguration

- **host**: IP-Adresse zum Binden (Standard: '0.0.0.0' für alle Interfaces)
- **port**: TCP-Port (Standard: 52381)
- **response_wait**: Maximale Wartezeit auf Kamera-Antwort in Sekunden (Standard: 0.3)

### Client-Verbindung

Verbinde dich mit dem Server über TCP:

```bash
# Mit netcat testen
echo "8101000601FF" | xxd -r -p | nc localhost 52381 | xxd -p
```

```python
# Mit Python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 52381))

# VISCA Befehl senden (z.B. Kamera einschalten)
sock.send(bytes.fromhex('8101040002FF'))

# Antwort empfangen
response = sock.recv(1024)
print(f"Response: {response.hex()}")

sock.close()
```

## VISCA Protokoll

VISCA-Befehle sind binär und enden immer mit `0xFF`:
- **Adresse**: Byte 1 (z.B. `0x81` für Kamera 1)
- **Command**: Bytes 2-N
- **Terminator**: `0xFF`

Beispiel-Befehle:
```
8101040002FF  - Power ON
8101040003FF  - Power OFF
8101060112FF  - Zoom Tele
8101060113FF  - Zoom Wide
```

## Statistiken

Statistiken können über die API abgerufen werden:

```bash
curl http://localhost:8081/api/stats
```

Response:
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
  }
}
```

## Unterschied zu UDP

- **TCP**: Zuverlässige Verbindung, automatisches Response-Handling, Session-basiert
- **UDP**: Verbindungslos, kein automatisches Response-Handling, für Sony VISCA-over-UDP mit speziellem Header

## Troubleshooting

### Port bereits in Verwendung

Falls Port 52381 bereits belegt ist, ändere `VISCA_TCP_PORT` in `main.py`:

```python
VISCA_TCP_PORT = 52382  # Oder einen anderen freien Port
```

Prüfe belegte Ports:
```bash
# Windows
netstat -an | findstr 52381

# Linux/macOS
lsof -i :52381
```

### Keine Verbindung möglich

1. Firewall-Regeln prüfen
2. Port-Freigabe prüfen
3. Logs in der Console beachten

### Kamera antwortet nicht

1. Serielle Verbindung prüfen (`/dev/ttyUSB0` oder COM-Port)
2. Baudrate prüfen (meist 9600)
3. `response_wait` erhöhen bei langsamer Kamera

## Logging

Der TCP-Server nutzt Python's logging-Modul:

```python
import logging
logging.basicConfig(level=logging.DEBUG)  # Für detaillierte Logs
```

Log-Levels:
- **INFO**: Verbindungen, Start/Stop
- **DEBUG**: Alle gesendeten/empfangenen Daten (Hex)
- **WARNING**: Nicht-kritische Fehler
- **ERROR**: Kritische Fehler
