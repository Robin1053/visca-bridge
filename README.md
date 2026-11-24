# visca-bridge

[![License](https://img.shields.io/github/license/Robin1053/visca-bridge)](https://github.com/Robin1053/visca-bridge/blob/master/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/Robin1053/visca-bridge)](https://github.com/Robin1053/visca-bridge/commits/master)
[![Open Issues](https://img.shields.io/github/issues/Robin1053/visca-bridge)](https://github.com/Robin1053/visca-bridge/issues)
[![Top language](https://img.shields.io/github/languages/top/Robin1053/visca-bridge)](https://github.com/Robin1053/visca-bridge)
[![Java](https://img.shields.io/badge/java-25%20LTS-orange)](https://openjdk.org/)

Visca-bridge soll eine schlanke VISCA-over-IP ↔ RS-232 Bridge werden. Dieser Branch enthält die
**Neuimplementierung in Java**. Sie ist noch in einem frühen Stadium.

> **Status:** Work in Progress. Aktuell nimmt der Server TCP-Verbindungen an, zerlegt den
> Datenstrom in VISCA-Nachrichten und gibt sie auf der Konsole aus. Eine Weiterleitung an die
> Kamera (RS-232) gibt es noch nicht.

## Projektaufbau

```
./
├── visca_bridge/                            # Maven-Projekt (Java 25)
│   ├── pom.xml
│   └── src/main/java/de/robineb/
│       ├── Main.java                        # Einstiegspunkt, startet den Server
│       ├── server/
│       │   └── ViscaIpServer.java           # TCP-Server, ein Virtual Thread pro Client
│       └── handler/
│           ├── ClientHandler.java           # Liest Daten eines Clients, zerlegt VISCA-Nachrichten
│           └── ViscaHandler.java            # Platzhalter für die VISCA-Verarbeitung
├── VISCA_TCP_README.md                      # Doku der früheren Python-Version
├── INTEGRATION_SUMMARY.md                   # Doku der früheren Python-Version
├── LICENSE
└── README.md
```

## Was schon funktioniert

- **TCP-Server** auf Port `10000` (fest in `Main.java` eingetragen)
- **Mehrere Clients gleichzeitig**: Jede Verbindung läuft in einem eigenen Virtual Thread (`ClientHandler`)
- **VISCA-Framing**: Eingehende Bytes werden gepuffert und am Terminator `0xFF` in einzelne
  Nachrichten zerlegt. Das funktioniert auch, wenn eine Nachricht über mehrere TCP-Pakete
  verteilt ankommt.
- **Debug-Ausgabe**: Rohdaten und erkannte VISCA-Nachrichten werden hexadezimal ausgegeben

## Voraussetzungen

- JDK 25 (LTS) oder neuer
- Maven 3.9+ (oder IntelliJ IDEA, das Maven-Projekt lässt sich direkt importieren)

## Bauen und Starten

```bash
cd visca_bridge
mvn compile
java -cp target/classes de.robineb.Main
```

Alternativ in IntelliJ IDEA `de.robineb.Main` direkt starten.

Ausgabe nach dem Start:

```
Hello and welcome to Visca Bridge!
Listening on port 10000 ...
```

## Testen

VISCA-Befehl per PowerShell senden (hier: Power ON):

```powershell
$client = [System.Net.Sockets.TcpClient]::new("localhost", 10000)
$bytes = [byte[]](0x81, 0x01, 0x04, 0x00, 0x02, 0xFF)
$client.GetStream().Write($bytes, 0, $bytes.Length)
$client.Close()
```

Oder unter Linux/macOS:

```bash
printf '\x81\x01\x04\x00\x02\xFF' | nc localhost 10000
```

Erwartete Server-Ausgabe:

```
Client connected: /127.0.0.1:54321
Received: 81 01 04 00 02 FF
VISCA: 81 01 04 00 02 FF
Client disconnected: /127.0.0.1:54321
```

## Geplant

- [ ] VISCA-Nachrichten in `ViscaHandler` auswerten
- [ ] Serielle Anbindung an die Kamera (RS-232)
- [ ] Kamera-Antworten an den Client zurücksenden
- [ ] VISCA-over-UDP (Sony-Format mit 8-Byte-Header, Port 52381)
- [ ] Konfigurierbare Ports und Serial-Parameter statt fest eingetragener Werte

## VISCA-Befehle (Beispiele)

Alle VISCA-Befehle sind hexadezimal und enden mit `FF`:

```
# Power
8101040002FF  - Power ON
8101040003FF  - Power OFF
8109040000FF  - Power Status Inquiry

# Zoom
8101040702FF  - Zoom Tele
8101040703FF  - Zoom Wide
8101040700FF  - Zoom Stop

# Pan/Tilt (VV = Pan-Speed, WW = Tilt-Speed)
81010601VVWW0303FF  - Stop
81010604FF          - Home

# Presets (pp = Preset-Nummer)
8101043F01ppFF  - Set Preset
8101043F02ppFF  - Recall Preset
```

## Lizenz

MIT License — siehe `LICENSE`.
