#!/usr/bin/env bash
set -euo pipefail

if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
	exec sudo -E bash "$0" "$@"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/home/Visca-Bridge/visca-bridge"
SERVICE_SRC="$SCRIPT_DIR/visca-bridge.service"

select_serial_port() {
	local devices=()
	local choice=""

	while IFS= read -r device; do
		devices+=("$device")
	done < <(
		{
			compgen -G "/dev/serial/by-id/*" || true
			compgen -G "/dev/ttyUSB*" || true
			compgen -G "/dev/ttyACM*" || true
		} | sort -u
	)

	echo
	if [[ ${#devices[@]} -eq 0 ]]; then
		read -r -p "Keine USB-Seriell-Geräte gefunden. Port manuell eingeben [/dev/ttyUSB0]: " choice
		printf '%s\n' "${choice:-/dev/ttyUSB0}"
		return
	fi

	echo "Verfügbare serielle Geräte:"
	for index in "${!devices[@]}"; do
		printf '  %d) %s\n' "$((index + 1))" "${devices[$index]}"
	done

	while true; do
		read -r -p "Gerät auswählen [1-${#devices[@]}] oder Pfad eingeben: " choice
		if [[ -z "$choice" ]]; then
			printf '%s\n' "${devices[0]}"
			return
		fi
		if [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#devices[@]} )); then
			printf '%s\n' "${devices[$((choice - 1))]}"
			return
		fi
		if [[ -e "$choice" ]]; then
			printf '%s\n' "$choice"
			return
		fi
		echo "Ungültige Eingabe."
	done
}

select_baudrate() {
	local choice=""

	while true; do
		read -r -p "Baudrate eingeben [9600]: " choice
		if [[ -z "$choice" ]]; then
			printf '%s\n' "9600"
			return
		fi
		if [[ "$choice" =~ ^[0-9]+$ ]]; then
			printf '%s\n' "$choice"
			return
		fi
		echo "Bitte eine numerische Baudrate eingeben."
	done
}

prompt_yes_no() {
	local prompt_text="$1"
	local default_answer="$2"
	local choice=""

	while true; do
		read -r -p "$prompt_text" choice
		choice="${choice:-$default_answer}"
		case "$choice" in
			j|J|ja|JA|Ja|y|Y|yes|YES|Yes)
				printf '%s\n' "yes"
				return
				;;
			n|N|nein|NEIN|Nein|no|NO|No)
				printf '%s\n' "no"
				return
				;;
			*)
				echo "Bitte mit ja oder nein antworten."
				;;
		esac
	done
}

configure_console_login() {
	local current_hostname
	local selected_hostname
	local banner_label
	local enable_autologin
	local primary_ip
	local color_cyan
	local color_green
	local color_yellow
	local color_reset

	current_hostname="$(hostname)"
	read -r -p "Hostname für Banner und System [${current_hostname}]: " selected_hostname
	selected_hostname="${selected_hostname:-$current_hostname}"

	read -r -p "Banner-Bezeichnung [VISCA Bridge]: " banner_label
	banner_label="${banner_label:-VISCA Bridge}"

	enable_autologin="$(prompt_yes_no "Root-Autologin auf tty1 aktivieren? [J/n]: " "yes")"

	if [[ "$selected_hostname" != "$current_hostname" ]]; then
		hostnamectl set-hostname "$selected_hostname"
	fi

	primary_ip="$(hostname -I 2>/dev/null | awk '{print $1}')"
	primary_ip="${primary_ip:-unbekannt}"

	color_cyan=$'\033[1;36m'
	color_green=$'\033[1;32m'
	color_yellow=$'\033[1;33m'
	color_reset=$'\033[0m'

	cat > /etc/issue <<EOF
${color_cyan}Debian GNU/Linux \s \r \l${color_reset}

${color_green}$selected_hostname tty1${color_reset}
${color_yellow}$selected_hostname login: root (automatic login)${color_reset}
EOF

	cat > /etc/motd <<EOF
${color_cyan}$banner_label${color_reset}

${color_green}Hostname:${color_reset} $selected_hostname
${color_yellow}IP Address:${color_reset} $primary_ip
EOF

	if [[ "$enable_autologin" == "yes" ]]; then
		mkdir -p /etc/systemd/system/getty@tty1.service.d
		cat > /etc/systemd/system/getty@tty1.service.d/autologin.conf <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin root --noclear %I \$TERM
EOF
		systemctl daemon-reload
		systemctl restart getty@tty1.service
	fi
}

apt update
apt install -y git python3 python3-pip python3-venv

if ! id -u Visca-Bridge >/dev/null 2>&1; then
	adduser --disabled-password --gecos "" --home /home/Visca-Bridge --shell /bin/bash Visca-Bridge
fi

usermod -aG dialout Visca-Bridge

mkdir -p /home/Visca-Bridge

if [[ "$SCRIPT_DIR" != "$INSTALL_DIR" ]]; then
	mkdir -p "$INSTALL_DIR"
	cp -a "$SCRIPT_DIR"/. "$INSTALL_DIR"/
fi

cd "$INSTALL_DIR"
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

SERIAL_PORT_SELECTED="$(select_serial_port)"
SERIAL_BAUDRATE_SELECTED="$(select_baudrate)"
cat > "$INSTALL_DIR/.env" <<EOF
VISCA_SERIAL_PORT=$SERIAL_PORT_SELECTED
VISCA_SERIAL_BAUDRATE=$SERIAL_BAUDRATE_SELECTED
EOF

configure_console_login

install -m 644 "$SERVICE_SRC" /etc/systemd/system/visca-bridge.service
systemctl daemon-reload
systemctl enable visca-bridge.service
systemctl restart visca-bridge.service