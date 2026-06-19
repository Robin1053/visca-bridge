# visca-bridge Roadmap

> Ein skalier- und wartbares Python-Backend für VISCA-Kamera-Steuerung

## Übersicht

Diese Roadmap gliedert sich in **4 Phasen**, die Codequalität, Testbarkeit, Features und Produktionsreife progressiv aufbauen. Jede Phase ist selbstständig abschließbar.

---

## Phase 1: Foundation – Code-Struktur & Qualität

**Ziel:** Wartbare, modulare Codebase mit professionellem Logging.

### 1.1 Modularisierung
- Teile `main.py` in logische Module auf:
  - `visca/config.py` – Konfigurationsmanagement (.env, Konstanten)
  - `visca/serial_bridge.py` – Serial-Port-Handling & Verbindung
  - `visca/tcp_server.py` – TCP-Server & Client-Verwaltung
  - `visca/protocol.py` – VISCA-Befehl-Parsing & Validierung
  - `visca/__init__.py` – Package-Init

- **Neue Struktur:**
  ```
  visca-bridge/
  ├── visca/
  │   ├── __init__.py
  │   ├── config.py
  │   ├── serial_bridge.py
  │   ├── tcp_server.py
  │   ├── protocol.py
  │   └── utils.py
  ├── main.py (nur Orchestrierung)
  ├── tests/ (siehe Phase 2)
  └── ...
  ```

### 1.2 Professionelles Logging
- Ersetze `log(level, msg)` durch Python `logging` Modul
- Features:
  - Log-Level via Env (`VISCA_LOG_LEVEL=DEBUG`)
  - Structured Logging (JSON optional für Production)
  - Log-Rotation (max 10 MB, 5 Backups)
  - Console + File Output

### 1.3 Robustheit & Error Handling
- Explizite Exception-Handling für:
  - Serial-Port-Fehler (Device nicht gefunden, Permissions)
  - TCP-Fehler (Port belegt, Connection dropped)
  - Timeout-Szenarien
- Graceful Shutdown: Cleanup bei `KeyboardInterrupt`, Signals (`SIGTERM`)
- Auto-Reconnect mit exponentiellem Backoff für Serial

### 1.4 Type Hints
- Alle Funktionen mit Type Annotations (Python 3.8+)
- Explizite Returntypen
- `mypy` Config erstellen

### 1.5 Deliverables
- [ ] Modularer Code mit klarer Separation of Concerns
- [ ] Logging-System implementiert
- [ ] Type Hints überall
- [ ] `mypy` läuft sauber
- [ ] README aktualisiert (neue Struktur)

---

## Phase 2: Qualitätssicherung & Testing

**Ziel:** Automatisierte Tests, vertrauenswürdiger Code.

### 2.1 Unit Tests
- Mock-Serial-Ports mit `unittest.mock`
- Test-Coverage für:
  - `config.py`: Env-Variablen, Defaults
  - `protocol.py`: VISCA-Befehle parsen (Power, Zoom, Pan/Tilt, etc.)
  - `tcp_server.py`: Client-Connections, Disconnects, Message-Routing
  - `serial_bridge.py`: Serial Read/Write, Timeouts

- **Struktur:**
  ```
  tests/
  ├── __init__.py
  ├── conftest.py (Fixtures)
  ├── test_config.py
  ├── test_protocol.py
  ├── test_tcp_server.py
  ├── test_serial_bridge.py
  └── fixtures/
      └── mock_responses.py
  ```

### 2.2 Integration Tests
- End-to-End mit `socat` (virtueller Serial-Port)
- Test: TCP-Client → Server → Serial → Response

### 2.3 Qualitäts-Tooling
- **`pytest`**: Test Runner
- **`pytest-cov`**: Coverage (Ziel: >80%)
- **`mypy`**: Type Checking
- **`pylint` / `flake8`**: Linting
- **`black`**: Code Formatting (optional)

### 2.4 CI/CD – GitHub Actions
- `.github/workflows/test.yml`:
  - Python 3.8, 3.9, 3.10, 3.11+
  - `pytest --cov=visca`
  - `mypy visca/`
  - `pylint visca/`
- Build Status Badge im README

### 2.5 Deliverables
- [ ] 30+ Unit Tests (80%+ Coverage)
- [ ] Integration Tests funktionieren
- [ ] GitHub Actions Workflow aktiv
- [ ] `requirements-dev.txt` (pytest, mypy, etc.)
- [ ] CONTRIBUTING.md mit Test-Guide

---

## Phase 3: Erweiterte Funktionalität

**Ziel:** Multi-Kamera, Persistierung, Metriken.

### 3.1 Multi-Kamera-Support
- `BridgeManager` verwaltet mehrere `SerialBridge`-Instanzen parallel
- Env-Config für mehrere Kameras:
  ```env
  VISCA_CAMERAS=camera1,camera2
  VISCA_CAMERA_camera1_PORT=/dev/ttyUSB0
  VISCA_CAMERA_camera1_BAUDRATE=9600
  VISCA_CAMERA_camera2_PORT=/dev/ttyUSB1
  VISCA_CAMERA_camera2_BAUDRATE=9600
  ```
- TCP-Routing: Client spezifiziert Kamera-ID oder Port

### 3.2 Preset-Management
- Persistierte Kamera-Positionen (Pan, Tilt, Zoom, Focus)
- Storage: JSON-Files oder SQLite
- Operations:
  - Preset speichern
  - Preset abrufen (Position wiederherstellen)
  - Preset-Liste laden

### 3.3 Status & Metriken
- Polling: Regelmäßiger Kamera-Status (Power, Zoom, Pan/Tilt)
- Gesammelte Metriken:
  - Uptime, aktive Clients, Commands/Sekunde
  - Letzte Fehler, Serial-Reconnects
  - Optional: Prometheus-Export (`/metrics`)

### 3.4 UDP-Support (optional)
- Asynchrones Protokoll (Fire-and-Forget)
- Nützlich für Status-Updates ohne Antwort-Garantie

### 3.5 Deliverables
- [ ] Multi-Kamera-Architektur getestet
- [ ] Preset-System funktioniert
- [ ] Metriken-Sammlung
- [ ] Integration Tests für neue Features
- [ ] Changelog aktualisiert

---

## Phase 4: Dokumentation & Wartbarkeit

**Ziel:** Klare API, vollständige Dokumentation, einfacher Betrieb.

### 4.1 Admin-Dashboard (optional)
- Einfache Web-UI (HTML/CSS/JS)
- Features:
  - Live-Status aller Kameras
  - Preset-Manager
  - Command-Sender (Hex-Input)
  - Logs-Viewer
  - System-Stats

### 4.2 Dokumentation
- **ARCHITECTURE.md**
  - High-Level Diagramm (Mermaid)
  - Datenfluss: Client → TCP → Serial → Kamera
  - Multi-Kamera-Routing-Logik
  
- **API.md**
  - TCP-Protokoll Dokumentation
  - VISCA-Befehl-Referenz (Power, Zoom, Pan/Tilt, Focus)
  - Verbindungs-Beispiele
  
- **CONTRIBUTING.md**
  - Setup (venv, deps, tests)
  - Code Style (black, mypy, pylint)
  - PR-Prozess
  
- **CHANGELOG.md**
  - Pro Release: Features, Bug-Fixes, Breaking Changes

### 4.3 Client-Libraries & Beispiele
- **Python Client Library** (`visca_client.py`)
  - Wrapper um TCP
  - Einfache API: `client.zoom_in()`, `client.get_status()`
  
- **Verbindungs-Beispiele**
  - In Dokumentation und README

### 4.4 Release & Versioning
- Semantic Versioning (1.0.0, 1.1.0, etc.)
- GitHub Release-Tags
- Changelog für jedes Release

### 4.5 Deliverables
- [ ] Admin-Dashboard (optional, aber sinnvoll)
- [ ] ARCHITECTURE.md mit Diagrammen
- [ ] API.md vollständig
- [ ] CONTRIBUTING.md
- [ ] Example Clients
- [ ] Build Status & Coverage Badges im README
- [ ] Release 1.0.0 auf GitHub

---

## Minimal Viable Release (MVR)

Wenn Ressourcen begrenzt:

1. Phase 1: Modularisierung + Logging (kurz)
2. Phase 2: Unit Tests + GitHub Actions
3. Phase 3: Multi-Kamera **oder** Presets (wähle eins)
4. Phase 4: ARCHITECTURE.md + API.md + CONTRIBUTING.md

= Solide, wartbares Projekt

---

## Operatives

### Commits & Git
- Aussagekräftige Commit-Messages mit Issue-Links
- GitHub Issues für Feature-Planning
- Pull Requests: Code-Review-Ready

### Badges im README
- Build Status (GitHub Actions)
- Coverage
- Python-Version Support
- License

### Nicht in Scope (bewusst ausgelassen)

- Docker (lokal auf einer Pi; nicht nötig)
- Cloud-Deployment (später optional)
- GUI auf Raspberry Pi (Web-UI ist portabler)
- Komplexe Infrastruktur (MQTT, Message Queues) – YAGNI
- REST API (Future: eigenes Projekt oder optional in Phase 4+)
