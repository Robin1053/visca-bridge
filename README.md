

# visca-bridge

[![License](https://img.shields.io/github/license/Robin1053/visca-bridge)](https://github.com/Robin1053/visca-bridge/blob/master/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/Robin1053/visca-bridge)](https://github.com/Robin1053/visca-bridge/commits/master)
[![Open Issues](https://img.shields.io/github/issues/Robin1053/visca-bridge)](https://github.com/Robin1053/visca-bridge/issues)
[![Repo size](https://img.shields.io/github/repo-size/Robin1053/visca-bridge)](https://github.com/Robin1053/visca-bridge)
[![Top language](https://img.shields.io/github/languages/top/Robin1053/visca-bridge)](https://github.com/Robin1053/visca-bridge)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)

Visca-bridge ist eine schlanke VISCA-over-IP ↔ RS-232 Bridge mit integriertem Frontend. Dieses Repository enthält das Python-Backend mit **TCP und UDP Server** sowie ein modernes Frontend unter `Frontend/` (Vite + React + TypeScript).

Kurz: Backend (Python) steuert die serielle Verbindung zur Kamera, das Frontend bietet eine Weboberfläche für Status & Steuerung.

## ✅ Aktueller Projektaufbau

```
./
├── main.py                      # Python-Backend (Haupt-Einstiegspunkt)
├── serial_transport.py          # Serielle Kommunikation mit Auto-Reconnect
├── visca_presets.py             # VISCA Preset Management
├── visca_udp_server.py          # UDP Server (Sony VISCA-over-UDP)
├── visca_tcp_server.py          # TCP Server (Standard VISCA-over-TCP)
├── test_tcp_client.py           # Test-Client für TCP-Server
├── presets.json                 # Preset-Konfiguration
├── VISCA_TCP_README.md          # Detaillierte TCP-Dokumentation
├── INTEGRATION_SUMMARY.md       # Änderungsübersicht
├── Frontend/                    # Vite + React TypeScript Frontend (Web UI)
└── README.md
```

## Hauptfunktionen

- **Duale Protokoll-Unterstützung**: 
  - **VISCA-over-TCP** (Port 52381) - Standard VISCA, Multi-Client Support
  - **VISCA-over-UDP** (Port 1259) - Sony VISCA mit Header-Stripping
- **Bidirektionale Bridge**: VISCA-over-IP ↔ RS-232
- **Multi-Client Support**: Mehrere TCP-Clients gleichzeitig
- **Automatisches Response-Handling**: Kamera-Antworten werden automatisch zurückgesendet
- **REST API**: Status, Statistiken und Preset-Verwaltung
- **Webinterface**: Moderne React-Oberfläche für Steuerung und Monitoring
- **Auto-Reconnect**: Automatische Wiederverbindung bei Serial-Problemen
- **Konfigurierbare Parameter**: Netzwerk, Serial, Timeouts

## Voraussetzungen

- Python 3.8+ (Backend)
- `pyserial` für serielle Hardware
- `Flask` für Web-API
- Node.js 16+ / npm oder pnpm (für das Frontend)

## Installation

1. Repository klonen:

```bash
git clone https://github.com/Robin1053/visca-bridge.git
cd visca-bridge
```

2. Python-Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

Oder manuell:

```bash
pip install pyserial flask
```

## Entwicklung — Backend (lokal)

1. (Optional) Erstelle ein virtuelles Environment und installiere Abhängigkeiten:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install pyserial flask
```

2. Backend starten:

```powershell
python main.py
```

Das Backend startet automatisch:
- **TCP Server** auf Port 52381 (Standard VISCA)
- **UDP Server** auf Port 1259 (Sony VISCA)
- **Flask Web-API** auf Port 8081

### Backend-Ausgabe

```
[INFO] [VISCA] Connected to /dev/ttyUSB0
[INFO] [UDP] VISCA UDP listening on :1259
[INFO] [TCP] VISCA TCP listening on 0.0.0.0:52381
[INFO] [TCP] Server thread started
 * Running on http://0.0.0.0:8081
```

### VISCA TCP testen

Mit dem mitgelieferten Test-Client:

```bash
python test_tcp_client.py localhost 52381
```

Oder manuell mit Python:

```python
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 52381))
sock.send(bytes.fromhex('8101040002FF'))  # Power ON
response = sock.recv(1024)
print(response.hex())
sock.close()
```

### REST API testen

```bash
# Statistiken abrufen
curl http://localhost:8081/api/stats

# Status-Seite
curl http://localhost:8081/
```

## Entwicklung — Frontend

Wechsel in das `Frontend`-Verzeichnis und installiere Abhängigkeiten:

```powershell
cd Frontend
npm install
npm run dev
```

Das Frontend läuft standardmäßig auf `http://localhost:5173` (Vite). In Produktion kannst du das Frontend bauen mit:

```powershell
npm run build
```

Die gebauten Dateien landen in `Frontend/dist` und können vom Backend oder einem separaten HTTP-Server ausgeliefert werden.

## Konfiguration

Backend-Parameter sind in `main.py` als Konstanten definiert:

```python
VISCA_IP_HOST = '0.0.0.0'        # Bind-Adresse für TCP/UDP
VISCA_UDP_PORT = 1259             # UDP Port (Sony VISCA-over-UDP)
VISCA_TCP_PORT = 52381            # TCP Port (Standard VISCA-over-TCP)
WEB_PORT = 8081                   # HTTP API Port
SERIAL_PORT = '/dev/ttyUSB0'     # Serial Port (Windows: 'COM3')
SERIAL_BAUDRATE = 9600            # Baudrate
RESPONSE_WAIT = 0.3               # Warte-Zeit auf Kamera-Antwort (Sek.)
```

**Hinweis für Windows**: Ändere `SERIAL_PORT` zu `'COM3'` (oder entsprechender COM-Port).

### Port-Übersicht

| Service | Port | Protokoll | Verwendung |
|---------|------|-----------|------------|
| VISCA TCP | 52381 | TCP | Standard VISCA, Multi-Client |
| VISCA UDP | 1259 | UDP | Sony VISCA-over-UDP mit Header |
| Web API | 8081 | HTTP | REST API, Status, Presets |
| Frontend | 5173 | HTTP | Vite Dev Server (nur Entwicklung) |

## Protokoll-Unterschiede: TCP vs UDP

### VISCA-over-TCP (Port 52381)
- ✅ Verbindungsorientiert und zuverlässig
- ✅ Automatisches Response-Handling
- ✅ Multi-Client Support (mehrere Controller gleichzeitig)
- ✅ Session-basiert
- ✅ Standard VISCA-Protokoll (kein Header)
- 🎯 **Empfohlen für die meisten Anwendungen**

### VISCA-over-UDP (Port 1259)
- Verbindungslos
- Kein automatisches Response-Handling
- Sony-spezifisches Format mit 8-Byte Header
- Header wird automatisch entfernt
- 🎯 **Nur für Sony-Kameras mit VISCA-over-UDP**

## Kurz-Anleitung für Raspberry Pi (Produktiv)

1. Python und Abhängigkeiten installieren:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip -y
cd /home/pi/visca-bridge
pip3 install pyserial flask
```

2. Serial-Port aktivieren mit `raspi-config` (Interface Options → Serial Port):
   - Login Shell über Serial: **Nein**
   - Serial Port Hardware: **Ja**

3. Port-Namen prüfen und in `main.py` anpassen:

```bash
ls -la /dev/tty* | grep USB
# Oder für onboard UART:
ls -la /dev/serial*
```

4. Test-Start:

```bash
python3 main.py
```

5. (Optional) Systemd-Service anlegen `/etc/systemd/system/visca-bridge.service`:

```ini
[Unit]
Description=VISCA Bridge - TCP/UDP to RS232
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/visca-bridge/main.py
WorkingDirectory=/home/pi/visca-bridge
Restart=always
RestartSec=5
User=pi

[Install]
WantedBy=multi-user.target
```

Service aktivieren:

```bash
sudo systemctl daemon-reload
sudo systemctl enable visca-bridge
sudo systemctl start visca-bridge
sudo systemctl status visca-bridge
```

Logs anzeigen:

```bash
sudo journalctl -u visca-bridge -f
```

## Fehlerbehebung & Tipps

### Serielle Verbindung

- **Keine Kamera-Reaktion**: 
  - TX/RX Pins vertauscht? 
  - Baudrate prüfen (Standard 9600)
  - `RESPONSE_WAIT` in `main.py` erhöhen (z.B. auf 0.5 oder 1.0)
  
- **Serial-Access auf Raspberry Pi**: 
  - Serielle Konsole muss deaktiviert sein
  - Hardware-Schnittstelle muss aktiviert sein
  - Benutzer zur `dialout` Gruppe hinzufügen: `sudo usermod -a -G dialout pi`

- **Port-Namen**:
  - Linux: `/dev/ttyUSB0`, `/dev/ttyAMA0`, `/dev/serial0`
  - Windows: `COM3`, `COM4`, etc.
  - macOS: `/dev/tty.usbserial-*`

### Netzwerk

- **TCP Port belegt**: 
  ```bash
  # Windows
  netstat -an | findstr 52381
  
  # Linux/macOS
  lsof -i :52381
  ```
  Lösung: Port in `main.py` ändern

- **Firewall**: Ports 52381 (TCP), 1259 (UDP), 8081 (HTTP) freigeben

- **Frontend nicht erreichbar**: 
  - Vite läuft standardmäßig auf Port 5173
  - Firewall/Port-Freigabe prüfen
  - CORS-Einstellungen prüfen

### TCP-Client

- **Verbindung wird abgelehnt**: Server läuft? Port korrekt?
- **Timeout beim Response**: `RESPONSE_WAIT` erhöhen
- **Keine Antwort**: Kamera eingeschaltet? Serial-Verbindung OK?

### Logging

Detaillierte Debug-Logs aktivieren in `main.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## VISCA-Befehle (Beispiele)

Alle VISCA-Befehle sind hexadezimal und enden mit `FF`:

```
# Power
8101040002FF  - Power ON
8101040003FF  - Power OFF
8109040000FF  - Power Status Inquiry

# Zoom
8101060112FF  - Zoom Tele
8101060113FF  - Zoom Wide
810104470pqrsFF - Zoom Position (p,q,r,s = Position)

# Pan/Tilt
81010601VVWWPPTTFF - Pan/Tilt (VV=Pan Speed, WW=Tilt Speed, PP=Pan, TT=Tilt)
8101060305FF  - Pan/Tilt Home
8101060313FF  - Pan/Tilt Stop

# Focus
8101040810FF  - Auto Focus ON
8101040802FF  - Manual Focus
8101060412FF  - Focus Far
8101060413FF  - Focus Near

# Presets
810104003FppFF - Recall Preset (pp = Preset Number 00-FE)
810104013FppFF - Set Preset (pp = Preset Number 00-FE)
```

Mehr Details: Siehe [VISCA_TCP_README.md](VISCA_TCP_README.md)

## API-Endpunkte

### GET /
Status-Seite mit Konfigurationsübersicht

### GET /api/stats
Server-Statistiken (TCP/UDP/Serial)

**Response:**
```json
{
  "tcp": {
    "host": "0.0.0.0",
    "port": 52381,
    "clients": 2,
    "total_connections": 15,
    "ip_to_rs232": 127,
    "rs232_to_ip": 127,
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

### POST /preset/advanced
Erweiterte Preset-Steuerung mit benutzerdefinierten Parametern

### POST /preset/virtual/{id}
Virtuelles Preset abrufen

## Weitere Dokumentation

- **[VISCA_TCP_README.md](VISCA_TCP_README.md)** - Detaillierte TCP-Server-Dokumentation
- **[INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)** - Übersicht der TCP-Integration
- **[test_tcp_client.py](test_tcp_client.py)** - Test-Client-Beispiele

## Architektur

```
┌─────────────────────────────────────────────────────────┐
│                     VISCA Bridge                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ TCP Server   │  │ UDP Server   │  │  Flask API   │ │
│  │ Port 52381   │  │ Port 1259    │  │  Port 8081   │ │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘ │
│         │                 │                            │
│         └────────┬────────┘                            │
│                  │                                     │
│         ┌────────▼────────┐                            │
│         │ Serial Transport│                            │
│         │  Auto-Reconnect │                            │
│         └────────┬────────┘                            │
│                  │                                     │
└──────────────────┼─────────────────────────────────────┘
                   │
                   ▼
            RS-232 (9600 baud)
                   │
                   ▼
           ┌──────────────┐
           │ VISCA Kamera │
           └──────────────┘
```

## Lizenz

MIT License — siehe `LICENSE`.

## Changelog

### Version 2.0 (Januar 2026)
- ✨ **NEU**: VISCA-over-TCP Server (Port 52381)
- ✨ Multi-Client Support für TCP-Verbindungen
- ✨ Automatisches Response-Handling
- ✨ REST API für Statistiken und Status
- ✨ Test-Client für TCP-Verbindungen
- 🔧 Modulare Architektur (separate Server-Dateien)
- 📚 Erweiterte Dokumentation

### Version 1.0
- VISCA-over-UDP Server (Sony Format)
- Serielle RS-232 Bridge
- React Frontend
- Preset-Management

---

**Datum der Aktualisierung:** 14/01/2026
