

# visca-bridge

[![License](https://img.shields.io/github/license/Robin1053/visca-bridge)](https://github.com/Robin1053/visca-bridge/blob/master/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/Robin1053/visca-bridge)](https://github.com/Robin1053/visca-bridge/commits/master)
[![Open Issues](https://img.shields.io/github/issues/Robin1053/visca-bridge)](https://github.com/Robin1053/visca-bridge/issues)
[![Repo size](https://img.shields.io/github/repo-size/Robin1053/visca-bridge)](https://github.com/Robin1053/visca-bridge)
[![Top language](https://img.shields.io/github/languages/top/Robin1053/visca-bridge)](https://github.com/Robin1053/visca-bridge)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)

Visca-bridge ist eine schlanke VISCA-over-IP ↔ RS-232 Bridge mit integriertem Frontend. Dieses Repository enthält das Python-Backend `visca_bridge.py` sowie ein modernes Frontend unter `Frontend/` (Vite + React + TypeScript).

Kurz: Backend (Python) steuert die serielle Verbindung zur Kamera, das Frontend bietet eine Weboberfläche für Status & Steuerung.

## ✅ Aktueller Projektaufbau

```
./
├── visca_bridge.py        # Python-Backend (Bridge, Webserver minimal)
├── Frontend/              # Vite + React TypeScript Frontend (Web UI)
└── README.md
```

## Hauptfunktionen

- Bidirektionale Bridge: VISCA-over-IP ↔ RS-232
- Webinterface zum Senden von Befehlen, Presets und zum Anzeigen von Logs
- Konfigurierbare Netzwerk- und serielle Parameter

## Voraussetzungen

- Python 3.8+ (Backend)
- Optional: `pyserial` wenn echte serielle Hardware genutzt wird
- Node.js 16+ / npm oder pnpm (für das Frontend)

## Entwicklung — Backend (lokal)

1. (Optional) Erstelle ein virtuelles Environment und installiere Abhängigkeiten:

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install --upgrade pip
pip install pyserial
```

2. Backend starten:

```powershell
python visca_bridge.py
```

Das Backend startet den minimalen Webserver und die VISCA-Bridge. Konfigurationsvariablen (IP/Port/Serial) liegen im Kopf der Datei `visca_bridge.py`.

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

- Backend-Parameter (Netzwerk, Serial, Ports) sind direkt in `visca_bridge.py` als Konstanten definiert.
- Frontend-Umgebungsvariablen: es gibt eine `Frontend/.env`-Datei im Repo — passe sie an, falls du API-URLs oder ähnliche Variablen überschreiben willst.

Beispiele (in `visca_bridge.py`):

```python
VISCA_IP_HOST = '0.0.0.0'
VISCA_IP_PORT = 1259
WEB_PORT = 8080
SERIAL_PORT = '/dev/serial0'
SERIAL_BAUDRATE = 9600
```

Hinweis: Auf Windows ändern sich seriellen Port-Namen (z.B. `COM3`).

## Kurz-Anleitung für Raspberry Pi (Produktiv)

1. Python, pyserial installieren:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip -y
pip3 install pyserial
```

2. Serial-Port aktivieren mit `raspi-config` (Interface Options → Serial Port)

3. (Optional) Systemd-Service anlegen `/etc/systemd/system/visca-bridge.service` und aktivieren:

```ini
[Unit]
Description=visca-bridge
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/visca-bridge/visca_bridge.py
WorkingDirectory=/home/pi/visca-bridge
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Dann:

```bash
sudo systemctl daemon-reload
sudo systemctl enable visca-bridge
sudo systemctl start visca-bridge
```

## Konflikte / Hinweis zur Repo-Historie

Während jüngster Wartungsarbeiten wurden lokale und entfernte Branch-Änderungen zusammengeführt; ein Backup-Branch `backup-local-20251112-1822` wurde lokal angelegt, bevor Konflikte aufgelöst wurden. Falls du vermutest, dass Änderungen fehlen, kannst du diesen Branch prüfen:

```powershell
git checkout backup-local-20251112-1822 -- visca_bridge.py
```

## Fehlerbehebung & Tipps

- Keine Kamera-Reaktion: TX/RX vertauscht? Baudrate prüfen (Standard 9600).
- Frontend nicht erreichbar: Vite läuft auf Port 5173 standardmäßig; überprüfe Firewall/Port.
- Serial-Access: Auf dem Pi muss die serielle Konsole deaktiviert und die Hardware-Schnittstelle aktiviert sein.

## Lizenz

MIT License — siehe `LICENSE` (sofern vorhanden).

---

Wenn du möchtest, kann ich die `README` weiter anreichern (z. B. detaillierte API-Dokumentation, Screenshots vom Frontend oder eine Beispielkonfiguration für `Frontend/.env`).

Datum der Aktualisierung: 2025-11-12
