# visca-bridge

[![License](https://img.shields.io/github/license/Robin1053/visca-bridge)](https://github.com/Robin1053/visca-bridge/blob/master/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/Robin1053/visca-bridge)](https://github.com/Robin1053/visca-bridge/commits/master)
[![Open Issues](https://img.shields.io/github/issues/Robin1053/visca-bridge)](https://github.com/Robin1053/visca-bridge/issues)
[![Repo size](https://img.shields.io/github/repo-size/Robin1053/visca-bridge)](https://github.com/Robin1053/visca-bridge)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)

Visca-bridge ist eine schlanke VISCA-over-IP ↔ RS-232 Bridge. Dieses Repository enthält das Python-Backend mit **TCP Server** sowie die serielle Anbindung.

Kurz: Backend (Python) steuert die serielle Verbindung zur Kamera und stellt Steuerung sowie Status über TCP bereit, UDP ist für später geplant.

## ✅ Aktueller Projektaufbau

```
./
├── main.py                      # Python-Backend
├── install.sh                   # Linux Install Script
├── requirements.txt             # Python Requirements file
└── README.md
```

## Hauptfunktionen

- **Protokoll-Unterstützung**: 
  - **VISCA-over-TCP** (Port 1259) - Standard VISCA, Multi-Client Support
- **Bidirektionale Bridge**: VISCA-over-IP ↔ RS-232
- **Multi-Client Support**: Mehrere TCP-Clients gleichzeitig
- **Automatisches Response-Handling**: Kamera-Antworten werden automatisch zurückgesendet
- **Auto-Reconnect**: Automatische Wiederverbindung bei Serial-Problemen
- **Konfigurierbare Parameter**: Netzwerk, Serial, Timeouts

## Voraussetzungen

- Python 3.8+ (Backend)
- `pyserial` für serielle Hardware

## Installation

### Automatischer Installer auf Debian/Linux

Wenn du das Projekt auf Debian oder einem Debian-basierten System einrichtest, kannst du den interaktiven Installer verwenden:

```bash
sudo bash install.sh
```

Der Installer liegt auch direkt als Raw-Datei auf GitHub:

```bash
https://raw.githubusercontent.com/Robin1053/visca-bridge/refs/heads/master/install.sh
```

Wenn du ihn direkt herunterladen und ausführen willst:

```bash
curl -fsSL https://raw.githubusercontent.com/Robin1053/visca-bridge/refs/heads/master/install.sh | bash
```

Der Installer fragt dabei nacheinander nach:

- seriellem Port oder USB-Gerät
- Baudrate
- Hostname für den Startbildschirm
- Banner-Bezeichnung
- optionalem Root-Autologin auf `tty1`

Die Auswahl wird in einer `.env` im Projektverzeichnis gespeichert, damit `main.py` beim Start automatisch den gewählten Port und die Baudrate verwendet.

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
pip install pyserial
```

## Entwicklung — Backend (lokal)

1. (Optional) Erstelle ein virtuelles Environment und installiere Abhängigkeiten:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install pyserial
```

2. Backend starten:

```powershell
python main.py
```

### Windows-Hinweise

Unter Windows gibt es keinen `install.sh`-Ablauf. Stattdessen:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Wenn du unter Windows keinen echten USB-Seriell-Adapter hast, kannst du zum Testen ein virtuelles COM-Port-Paar verwenden, zum Beispiel mit `com0com` oder einer ähnlichen Nullmodem-Lösung. Dann trägst du den passenden Port in der `.env` als `VISCA_SERIAL_PORT=COM3` ein.


Das Backend startet automatisch:
- **TCP Server** auf Port 1259 (Standard VISCA)
### Backend-Ausgabe

```
[INFO] [VISCA] Connected to /dev/ttyUSB0
[INFO] [TCP] VISCA TCP listening on :1259
[INFO] [TCP] Server thread started
```

### VISCA TCP testen

Manuell mit Python:

```python
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 1259))
sock.send(bytes.fromhex('8101040002FF'))  # Power ON
response = sock.recv(1024)
print(response.hex())
sock.close()
```

## Konfiguration

Die Laufzeitkonfiguration kann über eine `.env` im Projektverzeichnis gesetzt werden. Unterstützt werden aktuell:

```env
VISCA_SERIAL_PORT=/dev/ttyUSB0
VISCA_SERIAL_BAUDRATE=9600
```

Backend-Parameter sind in `main.py` als Konstanten definiert:

    ```python
    VISCA_IP_HOST = '0.0.0.0'         # Bind-Adresse für TCP
    VISCA_IP_PORT = 1259              # TCP Port (Standard VISCA-over-TCP)
    SERIAL_PORT = '/dev/ttyUSB0'      # Serial Port, alternativ aus .env (Windows: 'COM3')
    SERIAL_BAUDRATE = 9600            # Baudrate, alternativ aus .env
    RESPONSE_WAIT = 0.3               # Warte-Zeit auf Kamera-Antwort (Sek.)
    ```

**Hinweis für Windows**: Setze `VISCA_SERIAL_PORT=COM3` in der `.env` oder nutze den Installer nicht, sondern starte direkt mit einem passenden COM-Port.

### Port-Übersicht

| Service | Port | Protokoll | Verwendung |
|---------|------|-----------|------------|
| VISCA TCP | 1259 | TCP | Standard VISCA, Multi-Client |


### VISCA-over-TCP (Port 1259)
- ✅ Verbindungsorientiert und zuverlässig
- ✅ Automatisches Response-Handling
- ✅ Multi-Client Support (mehrere Controller gleichzeitig)
- ✅ Session-basiert
- ✅ Standard VISCA-Protokoll (kein Header)
- 🎯 **Empfohlen für die meisten Anwendungen**


## Kurz-Anleitung für Raspberry Pi (Produktiv)

1. Python und Abhängigkeiten installieren:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-venv python3-pip python3-serial -y
cd /home/pi/visca-bridge
```

2. Serial-Port aktivieren mit `raspi-config` (Interface Options → Serial Port):
   - Login Shell über Serial: **Nein**
   - Serial Port Hardware: **Ja**

3. Port-Namen prüfen und in `.env` anpassen:

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
oder aus Repository kopieren 
```bash
sudo cp ./visca-bridge.service /etc/systemd/system/visca-bridge.service
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

### Test ohne echte Hardware

- Linux/Debian: virtuelles PTY-Paar mit `socat`
- Windows: virtuelles COM-Port-Paar mit `com0com` oder ähnlicher Software
- In beiden Fällen kannst du den Port in der `.env` setzen und den TCP-Server normal starten

### Serielle Verbindung

- **Keine Kamera-Reaktion**: 
  - TX/RX Pins vertauscht? 
  - Baudrate prüfen (Standard 9600)
  - `RESPONSE_WAIT` in `main.py` erhöhen (z.B. auf 0.5 oder 1.0)
  
- **Serial-Access auf Raspberry Pi**: 
  - Serielle Konsole muss deaktiviert sein
  - Hardware-Schnittstelle muss aktiviert sein

- **Port-Namen**:
  - Linux: `/dev/ttyUSB0`, `/dev/ttyAMA0`, `/dev/serial0`
  - Windows: `COM3`, `COM4`, etc.
  - macOS: `/dev/tty.usbserial-*`

### Netzwerk

- **TCP Port belegt**: 
  ```bash
  # Windows
  netstat -an | findstr 1259
  
  # Linux/macOS
  lsof -i :1259
  ```
  Lösung: Port in `main.py` ändern
  
  - **Firewall**: Port 1259 (TCP) freigeben

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

## Changelog

### Version 2.0 (Juni 2026)
- ✨ Interaktiver Installer mit Port-, Baudraten- und tty1-Abfrage
- ✨ `.env`-Konfiguration für Serial-Port und Baudrate
- ✨ Farbiger tty1-Startbildschirm mit Hostname und IP
- ✨ Raw-Installer-Download von GitHub dokumentiert
- 📚 README auf den aktuellen Stand aktualisiert


### Version 1.0
- VISCA-over-TCP Server
- Serielle RS-232 Bridge

---

**Datum der Aktualisierung:** 16/06/2026
