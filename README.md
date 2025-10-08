
# 🎥 VISCA Bridge – Marshall CV620 Edition

**VISCA-over-IP ↔ RS-232 Bridge**  
Spezialversion für **Marshall CV620 PTZ-Kameras** – optimiert für den **Raspberry Pi Zero / Zero 2 W**.  
Ultra-leichtgewichtig, stabil, mit integriertem **Webinterface** und allen wichtigen CV620-Presets (Zoom, Fokus, PTZ, Presets usw.).

---

## ⚙️ Hauptfunktionen

- VISCA-over-IP ↔ RS-232 Bridge (bidirektional)
- Voll kompatibel mit **Marshall CV620** Befehlen
- Live-Webinterface mit Status, Logs und Befehlssteuerung
- Integrierte Presets:
  - Power On/Off, Zoom Tele/Wide, Fokus, PTZ, Preset Recall/Set usw.
- Kompaktes HTML-Frontend (`web/index.html`)
- Läuft stabil auf **Pi Zero 1 GHz / 512 MB RAM**

---

## 📁 Projektstruktur

```
visca_bridge_cv620/
├── visca_bridge_cv620.py    # Hauptskript
└── web/
    └── index.html           # Webinterface (Frontend)
```

---

## 🔧 Voraussetzungen

- Raspberry Pi OS Lite (empfohlen)
- Aktivierte serielle Schnittstelle
- Python 3 + PySerial

### Installation:

```bash
sudo apt update
sudo apt install python3 python3-serial -y
```
Serielle Schnittstelle aktivieren:
```bash
sudo raspi-config
# → Interface Options → Serial Port
# → Login Shell über Serial? → Nein
# → Serial Hardware aktivieren? → Ja
sudo reboot
```

---

## ▶️ Start

```bash
python3 visca_bridge_cv620.py
```

Beispielausgabe:
```
========================================
VISCA Bridge - CV620 Edition
========================================
[I] Serial: /dev/serial0@9600
[I] VISCA: 0.0.0.0:52381
[I] Web: http://0.0.0.0:8080
[I] VISCA Loop gestartet
```

---

## 🌐 Webinterface

Öffne im Browser:
```
http://<dein-pi>:8080/
```
**Funktionen:**
- Verbindungsstatus & Loganzeige
- Preset-Buttons für Zoom, Fokus, PTZ, Presets usw.
- Manuelle VISCA-Befehle als Hexcode senden

---

## ⚡ Konfiguration

Anpassbar im Kopf des Skripts:

```python
VISCA_IP_HOST = '0.0.0.0'      # IP-Adresse für Bridge
VISCA_IP_PORT = 52381          # VISCA TCP-Port
WEB_PORT = 8080                # Webserver-Port
SERIAL_PORT = '/dev/serial0'   # UART-Port
SERIAL_BAUDRATE = 9600         # Marshall CV620 Standard
MAX_LOG_ENTRIES = 50           # RAM-Schonung
```

---

## 🧠 CV620 VISCA-Presets

Beispiele aus `VISCA_PRESETS`:

| Kategorie | Aktion | Befehl (Hex) |
|------------|---------|--------------|
| Power | Power On | `81 01 04 00 02 FF` |
| Power | Power Off | `81 01 04 00 03 FF` |
| Zoom | Tele (Fast) | `81 01 04 07 27 FF` |
| Zoom | Wide (Fast) | `81 01 04 07 37 FF` |
| Focus | Auto | `81 01 04 38 02 FF` |
| Focus | One Push | `81 01 04 18 01 FF` |
| Pan/Tilt | Home | `81 01 06 04 FF` |
| Pan/Tilt | Stop | `81 01 06 01 18 18 03 03 FF` |
| Preset | Recall 1 | `81 01 04 3F 02 01 FF` |
| Preset | Set 1 | `81 01 04 3F 01 01 FF` |

Alle Kommandos sind **kompatibel mit der Marshall CV620**.

---

## 🔁 Autostart beim Booten

```bash
sudo nano /etc/systemd/system/visca_cv620.service
```
Inhalt:
```ini
[Unit]
Description=VISCA Bridge for Marshall CV620
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/visca_bridge_cv620/visca_bridge_cv620.py
WorkingDirectory=/home/pi/visca_bridge_cv620
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```
Dann aktivieren:
```bash
sudo systemctl daemon-reload
sudo systemctl enable visca_cv620
sudo systemctl start visca_cv620
```
Status prüfen:
```bash
sudo systemctl status visca_cv620
```

---

## 🧹 Fehlerbehebung

| Problem | Lösung |
|----------|---------|
| Keine Kamera-Reaktion | TX/RX vertauscht? Baudrate 9600? |
| Webinterface nicht erreichbar | Port 8080 belegt? |
| Kein Zugriff auf /dev/serial0 | Serial in `raspi-config` aktivieren |
| Kamera ignoriert Befehle | CV620 im **VISCA-Modus**, nicht IR oder Pelco-D? |
| CPU-Last zu hoch | `sleep()` in Loops erhöhen (aktuell 0.01 s) |

---

## 📄 Lizenz

MIT License – frei verwendbar und anpassbar.

---

## ❤️ Credits

Entwickelt für den **Raspberry Pi Zero**,  
getestet mit der **Marshall CV620 PTZ-Kamera**,  
mit Fokus auf minimale Latenz, niedrige CPU-Last und maximale Zuverlässigkeit.
