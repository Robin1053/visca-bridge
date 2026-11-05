#!/usr/bin/env bash
#
# visca-bridge Installer
#
# Funktioniert auf drei Wegen:
#   1. Aus dem geklonten Repo:   sudo bash install.sh
#   2. Direkt per curl:          curl -fsSL <raw-url>/install.sh | sudo bash
#   3. Per Prozess-Substitution: sudo bash <(curl -fsSL <raw-url>/install.sh)
#
# Liegt das Skript nicht neben main.py (Fall 2 und 3), wird das Repo
# automatisch von GitHub geholt. Eingaben werden immer von /dev/tty gelesen,
# damit die Abfragen auch funktionieren, wenn das Skript selbst über stdin kommt.
#
# Ohne Terminal (z. B. Automatisierung) werden die Defaults genommen; sie lassen
# sich per Umgebungsvariable vorgeben:
#   VISCA_SERIAL_PORT, VISCA_SERIAL_BAUDRATE, VISCA_HOSTNAME, VISCA_BANNER,
#   VISCA_AUTOLOGIN (yes/no), VISCA_REPO_URL, VISCA_REPO_BRANCH
#
# Alles steckt in main(), damit bash bei `curl | bash` erst das ganze Skript
# einliest, bevor irgendetwas ausgeführt wird (kein halb geladenes Skript bei
# Abbruch des Downloads, und kein Befehl kann den Rest des Skripts von stdin
# "wegessen").

set -euo pipefail

REPO_URL="${VISCA_REPO_URL:-https://github.com/Robin1053/visca-bridge.git}"
REPO_BRANCH="${VISCA_REPO_BRANCH:-master}"
RAW_URL="https://raw.githubusercontent.com/Robin1053/visca-bridge/refs/heads/${REPO_BRANCH}/install.sh"

INSTALL_USER="Visca-Bridge"
INSTALL_HOME="/home/${INSTALL_USER}"
INSTALL_DIR="${INSTALL_HOME}/visca-bridge"
ENV_FILE="${INSTALL_DIR}/.env"

# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

# Alle Meldungen gehen nach stderr. Funktionen, deren Ergebnis per $(...)
# abgefangen wird, dürfen auf stdout NUR den Rückgabewert schreiben.
msg()  { printf '%s\n' "$*" >&2; }
info() { printf '\033[1;36m==>\033[0m %s\n' "$*" >&2; }
warn() { printf '\033[1;33mWARNUNG:\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31mFEHLER:\033[0m %s\n' "$*" >&2; exit 1; }

# Gibt es ein Terminal, von dem wir lesen können?
has_tty() { ( exec </dev/tty ) 2>/dev/null; }

# ask "Prompt: " "default"  -> gibt Eingabe oder Default auf stdout aus
ask() {
	local prompt="$1" default="$2" reply=""
	if has_tty; then
		read -r -p "$prompt" reply </dev/tty || reply=""
	fi
	printf '%s\n' "${reply:-$default}"
}

# Wert aus einer bestehenden .env lesen (für Neuinstallation/Update als Default)
env_get() {
	local key="$1"
	[[ -f "$ENV_FILE" ]] || return 0
	sed -n "s/^${key}=//p" "$ENV_FILE" | tail -n 1
}

is_number() { [[ "$1" =~ ^[0-9]+$ ]] && (( "$1" > 0 )); }

# ---------------------------------------------------------------------------
# Root-Rechte
# ---------------------------------------------------------------------------

ensure_root() {
	[[ ${EUID:-$(id -u)} -eq 0 ]] && return 0

	local self="${BASH_SOURCE[0]:-}"
	if [[ -n "$self" && -f "$self" ]]; then
		# Normaler Fall: Skript liegt als Datei vor
		exec sudo -H bash "$self" "$@"
	fi

	# Skript kam über eine Pipe (curl ... | bash) -> $0 ist nur "bash",
	# es gibt keine Datei zum Neustarten. Also nochmal laden und mit sudo starten.
	command -v curl >/dev/null 2>&1 || die "Bitte mit sudo starten: curl -fsSL $RAW_URL | sudo bash"
	local tmp
	tmp="$(mktemp /tmp/visca-bridge-install.XXXXXX.sh)"
	curl -fsSL "$RAW_URL" -o "$tmp" || die "Konnte Installer nicht laden: $RAW_URL"
	exec sudo -H bash "$tmp" "$@"
}

# ---------------------------------------------------------------------------
# Quellcode bereitstellen
# ---------------------------------------------------------------------------

fetch_sources() {
	local self="${BASH_SOURCE[0]:-}" script_dir=""
	if [[ -n "$self" && -f "$self" ]]; then
		script_dir="$(cd "$(dirname "$self")" && pwd)"
	fi

	mkdir -p "$INSTALL_DIR"

	if [[ -n "$script_dir" && -f "$script_dir/main.py" && -f "$script_dir/visca-bridge.service" ]]; then
		if [[ "$script_dir" != "$INSTALL_DIR" ]]; then
			info "Kopiere Projekt aus $script_dir nach $INSTALL_DIR"
			cp -a "$script_dir"/. "$INSTALL_DIR"/
		fi
		return
	fi

	# Kein Repo neben dem Skript -> von GitHub holen.
	# In ein Temp-Verzeichnis klonen und drüberkopieren, damit eine bestehende
	# .env und das venv erhalten bleiben (Update-Fall).
	info "Lade visca-bridge ($REPO_BRANCH) von $REPO_URL"
	local tmp_clone
	tmp_clone="$(mktemp -d /tmp/visca-bridge-src.XXXXXX)"
	git clone --quiet --depth 1 --branch "$REPO_BRANCH" "$REPO_URL" "$tmp_clone" \
		|| die "git clone fehlgeschlagen"
	cp -a "$tmp_clone"/. "$INSTALL_DIR"/
	rm -rf "$tmp_clone"
}

# ---------------------------------------------------------------------------
# Abfragen
# ---------------------------------------------------------------------------

select_serial_port() {
	local devices=() device choice default

	while IFS= read -r device; do
		[[ -n "$device" ]] && devices+=("$device")
	done < <(
		{
			compgen -G "/dev/serial/by-id/*" || true
			compgen -G "/dev/ttyUSB*" || true
			compgen -G "/dev/ttyACM*" || true
		} | sort -u
	)

	# Default: Umgebungsvariable > bestehende .env > erstes Gerät > /dev/ttyUSB0
	default="${VISCA_SERIAL_PORT:-$(env_get VISCA_SERIAL_PORT)}"
	if [[ -z "$default" ]]; then
		default="${devices[0]:-/dev/ttyUSB0}"
	fi

	msg ""
	if [[ ${#devices[@]} -eq 0 ]]; then
		warn "Keine USB-Seriell-Geräte gefunden (Adapter angesteckt? -> lsusb, dmesg)."
		ask "Port manuell eingeben [$default]: " "$default"
		return
	fi

	msg "Verfügbare serielle Geräte:"
	local i
	for i in "${!devices[@]}"; do
		msg "  $((i + 1))) ${devices[$i]}"
	done

	while true; do
		choice="$(ask "Gerät auswählen [1-${#devices[@]}] oder Pfad eingeben [$default]: " "$default")"
		if [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#devices[@]} )); then
			printf '%s\n' "${devices[$((choice - 1))]}"
			return
		fi
		if [[ "$choice" == /dev/* ]]; then
			[[ -e "$choice" ]] || warn "$choice existiert (noch) nicht - wird trotzdem übernommen."
			printf '%s\n' "$choice"
			return
		fi
		msg "Ungültige Eingabe."
		has_tty || { printf '%s\n' "$default"; return; }
	done
}

select_baudrate() {
	local choice default

	default="${VISCA_SERIAL_BAUDRATE:-$(env_get VISCA_SERIAL_BAUDRATE)}"
	is_number "${default:-x}" || default="9600"

	while true; do
		choice="$(ask "Baudrate eingeben [$default]: " "$default")"
		if is_number "$choice"; then
			printf '%s\n' "$choice"
			return
		fi
		msg "Bitte eine numerische Baudrate eingeben (z. B. 9600)."
		has_tty || { printf '%s\n' "$default"; return; }
	done
}

prompt_yes_no() {
	local prompt_text="$1" default_answer="$2" choice
	while true; do
		choice="$(ask "$prompt_text" "$default_answer")"
		case "$choice" in
			j|J|ja|JA|Ja|y|Y|yes|YES|Yes) printf 'yes\n'; return ;;
			n|N|nein|NEIN|Nein|no|NO|No)  printf 'no\n';  return ;;
			*)
				msg "Bitte mit ja oder nein antworten."
				has_tty || { printf '%s\n' "$default_answer"; return; }
				;;
		esac
	done
}

# ---------------------------------------------------------------------------
# Konsole / Hostname
# ---------------------------------------------------------------------------

set_hostname() {
	local old="$1" new="$2"
	[[ "$new" == "$old" ]] && return
	hostnamectl set-hostname "$new"
	# Sonst meckert sudo "unable to resolve host ..."
	if grep -qE '^127\.0\.1\.1[[:space:]]' /etc/hosts; then
		sed -i -E "s/^127\.0\.1\.1[[:space:]].*/127.0.1.1\t${new}/" /etc/hosts
	else
		printf '127.0.1.1\t%s\n' "$new" >> /etc/hosts
	fi
}

configure_console_login() {
	local current_hostname selected_hostname banner_label enable_autologin primary_ip
	local c_cyan=$'\033[1;36m' c_green=$'\033[1;32m' c_yellow=$'\033[1;33m' c_reset=$'\033[0m'

	current_hostname="$(hostname)"
	selected_hostname="$(ask "Hostname für Banner und System [${VISCA_HOSTNAME:-$current_hostname}]: " "${VISCA_HOSTNAME:-$current_hostname}")"
	banner_label="$(ask "Banner-Bezeichnung [${VISCA_BANNER:-VISCA Bridge}]: " "${VISCA_BANNER:-VISCA Bridge}")"
	enable_autologin="$(prompt_yes_no "Root-Autologin auf tty1 aktivieren? [J/n]: " "${VISCA_AUTOLOGIN:-yes}")"

	set_hostname "$current_hostname" "$selected_hostname"

	primary_ip="$(hostname -I 2>/dev/null | awk '{print $1}')"
	primary_ip="${primary_ip:-unbekannt}"

	cat > /etc/issue <<EOF
${c_cyan}Debian GNU/Linux \s \r \l${c_reset}

${c_green}$selected_hostname tty1${c_reset}
EOF

	cat > /etc/motd <<EOF
${c_cyan}$banner_label${c_reset}

${c_green}Hostname:${c_reset} $selected_hostname
${c_yellow}IP Address:${c_reset} $primary_ip
EOF

	local autologin_conf=/etc/systemd/system/getty@tty1.service.d/autologin.conf
	if [[ "$enable_autologin" == "yes" ]]; then
		printf '%s\n' "${c_yellow}$selected_hostname login: root (automatic login)${c_reset}" >> /etc/issue
		mkdir -p "$(dirname "$autologin_conf")"
		cat > "$autologin_conf" <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin root --noclear %I \$TERM
EOF
	else
		rm -f "$autologin_conf"
	fi
	systemctl daemon-reload
	systemctl restart getty@tty1.service || true
}

# ---------------------------------------------------------------------------
# Ablauf
# ---------------------------------------------------------------------------

cleanup() {
	# Vom Pipe-Modus heruntergeladene Kopie des Installers wieder entfernen
	local self="${BASH_SOURCE[0]:-}"
	if [[ "$self" == /tmp/visca-bridge-install.* ]]; then
		rm -f "$self"
	fi
}

main() {
	ensure_root "$@"
	trap cleanup EXIT

	info "Installiere Systempakete"
	apt-get update
	apt-get install -y git python3 python3-pip python3-venv ca-certificates </dev/null

	if ! id -u "$INSTALL_USER" >/dev/null 2>&1; then
		info "Lege Benutzer $INSTALL_USER an"
		adduser --disabled-password --gecos "" --home "$INSTALL_HOME" --shell /bin/bash "$INSTALL_USER" </dev/null
	fi
	usermod -aG dialout "$INSTALL_USER"

	fetch_sources

	info "Richte Python-venv ein"
	cd "$INSTALL_DIR"
	python3 -m venv venv
	./venv/bin/pip install --quiet --upgrade pip
	./venv/bin/pip install --quiet -r requirements.txt

	info "Serielle Schnittstelle konfigurieren"
	local serial_port serial_baud
	serial_port="$(select_serial_port)"
	serial_baud="$(select_baudrate)"

	cat > "$ENV_FILE" <<EOF
VISCA_SERIAL_PORT=$serial_port
VISCA_SERIAL_BAUDRATE=$serial_baud
EOF

	info "Konsole konfigurieren"
	configure_console_login

	chown -R "$INSTALL_USER:$INSTALL_USER" "$INSTALL_DIR"
	chmod 600 "$ENV_FILE"

	info "Installiere systemd-Service"
	install -m 644 "$INSTALL_DIR/visca-bridge.service" /etc/systemd/system/visca-bridge.service
	systemctl daemon-reload
	systemctl enable visca-bridge.service
	systemctl restart visca-bridge.service

	msg ""
	info "Fertig."
	msg "  Konfiguration: $ENV_FILE"
	msg "    VISCA_SERIAL_PORT=$serial_port"
	msg "    VISCA_SERIAL_BAUDRATE=$serial_baud"
	[[ -e "$serial_port" ]] || warn "$serial_port existiert nicht - der Service startet erst, wenn der Adapter erkannt wird."
	msg "  Status: systemctl status visca-bridge"
	msg "  Logs:   journalctl -u visca-bridge -f"
}

main "$@"
