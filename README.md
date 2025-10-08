# 🎥 VISCA Bridge – Raspberry Pi Zero Edition (Marshall CV620)

**Ultra-leichte VISCA-over-IP ↔ RS-232 Bridge**  
speziell für **Marshall CV620** PTZ-Kameras entwickelt.  
Optimiert für den **Raspberry Pi Zero / Zero 2 W** mit minimalem RAM- und CPU-Verbrauch  
und integriertem Webinterface zur Steuerung, Statusanzeige und Diagnose.

---

## ⚙️ Funktionen

- VISCA-over-IP ↔ RS-232 Bridge (bidirektional)
- Voll kompatibel mit **Marshall CV620**, inkl. Power-, Home- & Query-Befehlen
- Minimalistisches **Web-UI**
- Live-Status & Logs
- Manuelle Hex-Befehle senden
- Presets: Power On/Off, Home Position, Query
- Optimiert für **geringe Last auf Pi Zero**

---

## 📁 Projektstruktur

```
visca_bridge/
├── visca_bridge.py        # Hauptskript
└── web/
    └── index.html         # Webinterface (Frontend)
```

---

## 🔧 Installation

### 1. Voraussetzungen

- Raspberry Pi OS Lite (empfohlen)
- Python 3 installiert:
  ```bash
  sudo apt update
  sudo apt install python3 python3-serial -y
  ```

### 2. Projekt klonen oder kopieren

```bash
git clone https://github.com/<dein-user>/visca-bridge.git
cd visca-bridge
```

### 3. Serielle Schnittstelle aktivieren

```bash
sudo raspi-config
```
- **Interface Options → Serial Port**
  - **Login Shell über Serial?** → *Nein*
  - **Serial Hardware aktivieren?** → *Ja*

Danach neu starten:
```bash
sudo reboot
```

---

## ▶️ Starten

```bash
python3 visca_bridge.py
```

Beispielausgabe:
```
========================================
VISCA Bridge - Marshall CV620
========================================
[I] Serial: /dev/serial0@9600
[I] VISCA: 0.0.0.0:52381
[I] Web: http://0.0.0.0:8080
[I] VISCA Loop gestartet
```

---

## 🌐 Webinterface

Im Browser öffnen:  
👉 `http://<dein-pi>:8080/`

Du siehst:
- Systemstatus (Bridge & Kamera)
- Letzte Log-Einträge
- Hex-Eingabe für Befehle
- Schnellzugriff für gängige **CV620 VISCA-Kommandos**

---

## ⚡ Konfiguration

In `visca_bridge.py` oben anpassbar:

```python
VISCA_IP_HOST = '0.0.0.0'    # IP-Serveradresse
VISCA_IP_PORT = 52381        # VISCA-Port
WEB_PORT = 8080              # Webserver-Port
SERIAL_PORT = '/dev/serial0' # RS232-Interface
SERIAL_BAUDRATE = 9600       # Baudrate (Marshall CV620 Standard)
MAX_LOG_ENTRIES = 50         # Loggröße (RAM sparen)
```

---

## 🧠 Steuerbefehle (Marshall CV620)

| Aktion             | VISCA-Hex-Befehl              | Beschreibung |
|--------------------|------------------------------|---------------|
| Power On           | `81 01 04 00 02 FF` | Kamera einschalten |
| Power Off          | `81 01 04 00 03 FF` | Kamera ausschalten |
| Query Power State  | `81 09 04 00 FF`     | Status abfragen |
| Home Position      | `81 01 06 01 FF`     | Kamera zentrieren |
| Pan/Tilt Stop      | `81 01 06 01 00 00 03 01 FF` | Bewegung stoppen |

Alle Hex-Befehle sind **kompatibel zur CV620** und können im Web-UI manuell eingegeben oder automatisiert gesendet werden.

---

## 🔁 Autostart beim Booten (optional)

```bash
sudo nano /etc/systemd/system/visca.service
```

Inhalt:
```ini
[Unit]
Description=VISCA Bridge for Marshall CV620
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/visca_bridge/visca_bridge.py
WorkingDirectory=/home/pi/visca_bridge
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Dann aktivieren:
```bash
sudo systemctl daemon-reload
sudo systemctl enable visca
sudo systemctl start visca
```

Status prüfen:
```bash
sudo systemctl status visca
```

---

## 🧹 Fehlerbehebung

| Problem | Lösung |
|----------|---------|
| Kein Zugriff auf `/dev/serial0` | Prüfe `raspi-config` → Serial aktiviert? |
| Webinterface lädt nicht | Port 8080 bereits belegt? Anderen `WEB_PORT` wählen |
| CV620 reagiert nicht | TX/RX-Leitungen gekreuzt? Baudrate korrekt (9600)? |
| Keine Power-Reaktion | Kamera im VISCA-Modus? Prüfe CV620 Menü |
| Hohe CPU-Last | Andere Prozesse blockieren Serial? Prüfe per `top` |

---

## 📄 Lizenz

MIT License – frei verwendbar, modifizierbar und erweiterbar.

---

## ❤️ Credits

Entwickelt für den **Raspberry Pi Zero**,  
spezifisch getestet mit der **Marshall CV620 PTZ-Kamera**,  
optimiert für maximale Effizienz bei minimalem Overhead.  
Kompatibel mit allen VISCA-basierten Steuerungen über RS-232.
