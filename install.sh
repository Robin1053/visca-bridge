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
cat > "$INSTALL_DIR/.env" <<EOF
VISCA_SERIAL_PORT=$SERIAL_PORT_SELECTED
EOF

install -m 644 "$SERVICE_SRC" /etc/systemd/system/visca-bridge.service
systemctl daemon-reload
systemctl enable visca-bridge.service
systemctl restart visca-bridge.service