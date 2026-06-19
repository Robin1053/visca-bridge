# visca-bridge

[![License](https://img.shields.io/github/license/Robin1053/visca-bridge)](https://github.com/Robin1053/visca-bridge/blob/master/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/Robin1053/visca-bridge)](https://github.com/Robin1053/visca-bridge/commits/master)
[![Open Issues](https://img.shields.io/github/issues/Robin1053/visca-bridge)](https://github.com/Robin1053/visca-bridge/issues)
[![Repo size](https://img.shields.io/github/repo-size/Robin1053/visca-bridge)](https://github.com/Robin1053/visca-bridge)
[![Python](https://img.shields.io/badge/python-3.9-cyan)](https://www.python.org/)
[![Build Status](https://img.shields.io/badge/build-placeholder-lightgrey)](https://github.com/Robin1053/visca-bridge/actions)
[![Coverage](https://img.shields.io/badge/coverage-placeholder-lightgrey)](CHANGELOG.md)

visca-bridge ist ein schlankes, wartbares Python-Backend, das VISCA-over-TCP mit einer seriellen RS-232-Kamera verbindet. Fokus: Stabilität, einfache Konfiguration und zuverlässiges Proxying von VISCA-Befehlen.

## Quick Start

Kurz: Clone → virtuelles Environment → Abhängigkeiten installieren → starten

```bash
git clone https://github.com/Robin1053/visca-bridge.git
cd visca-bridge
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python main.py
```

Hinweis: Python 3.9+ wird empfohlen.

## Projektstruktur (aktuell)

```
./
├── main.py                      # Orchestrierung / Einstiegspunkt
├── pyproject.toml               # Projektmetadaten, Dependencies
├── ROADMAP.md                   # Projekt-Roadmap
├── CHANGELOG.md                 # Release-Historie
├── README.md
├── install.sh                   # Optionaler Installer für Raspberry Pi
└── ...
```

## Hauptfunktionen

- **VISCA-over-TCP** (Port 1259) — Standard VISCA, Multi-Client Support
- **Bidirektionale Bridge**: VISCA-over-IP ↔ RS-232
- **Multi-Client Support**: Mehrere TCP-Clients gleichzeitig
- **Synchronous Response Handling**: Kamera-Antworten werden bei Bedarf zurückgeleitet
- **Auto-Reconnect**: Wiederverbindung bei Serial-Problemen mit Backoff
- **Konfigurierbare Parameter**: Netzwerk, Serial, Timeouts via `.env` oder Umgebungsvariablen

## Voraussetzungen

- Python 3.9+ (empfohlen)
- `pyserial` für serielle Hardware (wird über `pyproject.toml` installiert)

## Installation

Es gibt zwei typische Wege:

1) Production (Raspberry Pi / System-Installation)

```bash
sudo bash install.sh
```

Der Installer erstellt eine `.env` im Projektverzeichnis und nimmt einige Einstellungen entgegen (Serial-Port, Baudrate, Hostname).

2) Development (lokal, für Contributor)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Das installiert die Laufzeit-Abhängigkeiten sowie Dev-Extras (pytest, mypy, black).

## Entwicklung — Backend (lokal)

Nach dem Setup (`pip install -e .[dev]`) kannst du testen und entwickeln:

Starten in der Entwicklung:

```bash
source .venv/bin/activate
python main.py
```

Tests ausführen:

```bash
pytest
```

Weitere Dev-Kommandos (Lint, Type-Check):

```bash
black .
mypy visca/
pylint visca/
```

Hinweis für Windows: Erstelle ein venv und aktiviere es mit PowerShell (Activate.ps1). Für virtuelle COM-Ports unter Windows nutze `com0com`.

Das Backend startet standardmässig den TCP-Server auf Port 1259.

## Konfiguration

Laufzeitkonfiguration erfolgt über eine `.env` im Projektverzeichnis oder über Umgebungsvariablen. Beispiele:

```env
VISCA_SERIAL_PORT=/dev/ttyUSB0
VISCA_SERIAL_BAUDRATE=9600
VISCA_IP_PORT=1259
VISCA_LOG_LEVEL=INFO
```

Default-Parameter (konfigurierbar):

```python
VISCA_IP_HOST = '0.0.0.0'
VISCA_IP_PORT = 1259
SERIAL_PORT = '/dev/ttyUSB0'
SERIAL_BAUDRATE = 9600
RESPONSE_WAIT = 0.3
```

Windows: Setze `VISCA_SERIAL_PORT=COM3` in der `.env` oder verwende ein entsprechendes virtuelles COM-Paar.

### VISCA TCP testen

Mit Python (TCP) kannst du manuell Befehle senden:

```python
import socket
sock = socket.socket()
sock.connect(('localhost', 1259))
sock.send(bytes.fromhex('8101040002FF'))  # Power ON
print(sock.recv(1024).hex())
sock.close()
```

### Port-Übersicht

| Service | Port | Protokoll | Verwendung |
|---------|------|-----------|------------|
| VISCA TCP | 1259 | TCP | Standard VISCA, Multi-Client |

## Raspberry Pi — Produktivbetrieb

Empfohlene Schritte auf einem Raspberry Pi:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-venv python3-pip python3-serial -y
cd /home/pi/visca-bridge
```

Serial-Port in raspi-config aktivieren (Interface → Serial Port):
- Login Shell über Serial: **Nein**
- Serial Port Hardware: **Ja**

Ports prüfen:

```bash
ls -la /dev/tty* | grep USB
ls -la /dev/serial*
```

Start (Test):

```bash
python3 main.py
```

Optional: Systemd-Service (angepassten Pfad verwenden):

```ini
[Unit]
Description=VISCA Bridge - TCP to RS232
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

Logs anschauen:

```bash
sudo journalctl -u visca-bridge -f
```

## Fehlerbehebung & Tipps

### Test ohne echte Hardware

- Linux/Debian: virtuelles PTY-Paar mit `socat`
- Windows: virtuelles COM-Port-Paar mit `com0com`

Stelle in beiden Fällen den virtuellen Port in `.env` ein.

### Serielle Verbindung

- **Keine Kamera-Reaktion**: TX/RX vertauscht, falsche Baudrate, Kamera aus
- **Serial-Access auf Raspberry Pi**: Serielle Konsole deaktivieren, Hardware aktivieren
- **Port-Namen**: Linux `/dev/ttyUSB0`, Windows `COM3`, macOS `/dev/tty.usbserial-*`

### Netzwerk

Wenn Port 1259 belegt:

```bash
lsof -i :1259
# oder (Windows)
netstat -an | findstr 1259
```

### Logging

Nutze die integrierte Logging-Konfiguration (siehe `pyproject.toml` und `config`-Modul nach Refactor). Für schnelle Debug-Runs:

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

## Architektur

```
┌────────────────────────────────────────────────────────┐
│                     VISCA Bridge                       │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────────┐                                      │
│  │ TCP Server   │                                      │
│  │ Port 1259    │                                      │
│  └──────┬───────┘                                      │
│         │                                              │
│         └────────┐                                     │
│                  │                                     │
│         ┌────────▼──────────────────────────┐          │
│         │          Serial Layer             │          │
│         │     .env, Port-Auswahl, Auto-     │          │
│         │     Reconnect, Baudrate           │          │
│         └────────┬──────────────────────────┘          │
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

Weiterführende Links

- ROADMAP: `ROADMAP.md`
- CHANGELOG: `CHANGELOG.md`
- CONTRIBUTING: `CONTRIBUTING.md` (wird ergänzt)
- ARCHITECTURE: `ARCHITECTURE.md` (wird ergänzt)
