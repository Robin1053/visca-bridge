from flask import Flask, request, jsonify
from serial_transport import SerialViscaTransport
from visca_presets import ViscaPresetsCV620
from visca_udp_server import ViscaUDPServer
from visca_tcp_server import ViscaTCPServer
import logging
import socket


VISCA_IP_HOST = '0.0.0.0'
VISCA_UDP_PORT = 1259  # UDP Port für VISCA over UDP
VISCA_TCP_PORT = 52381  # TCP Port für VISCA over TCP
WEB_PORT = 8081
SERIAL_PORT = '/dev/ttyUSB0'
SERIAL_BAUDRATE = 9600
SERIAL_TIMEOUT = 1.0  # Erhöht von 0.1 auf 1.0 Sekunde
MAX_LOG_ENTRIES = 100
RESPONSE_WAIT = 0.3  # Zeit auf Kamera-Antwort warten

# Globale Variablen
visca_socket = None

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

transport = SerialViscaTransport("/dev/ttyUSB0")
presets = ViscaPresetsCV620(transport)

# UDP Server starten (für Sony VISCA over UDP)
udp_server = ViscaUDPServer(
    transport=transport,
    port=VISCA_UDP_PORT,
    sony_udp=True
)
udp_server.start()

# TCP Server starten (für standard VISCA over TCP)
tcp_server = ViscaTCPServer(
    transport=transport,
    host=VISCA_IP_HOST,
    port=VISCA_TCP_PORT,
    response_wait=RESPONSE_WAIT
)
tcp_server.start()


@app.route("/preset/advanced", methods=["POST"])
def preset_advanced():
    data = request.json
    presets.recall_advanced(data)
    return jsonify({"status": "ok"})


@app.route("/preset/virtual/<int:preset_id>", methods=["POST"])
def preset_virtual(preset_id):
    presets.recall_virtual(preset_id)
    return jsonify({"status": "ok"})


@app.route("/api/stats", methods=["GET"])
def api_stats():
    """Gibt Statistiken über TCP/UDP Server zurück"""
    tcp_stats = tcp_server.get_stats()
    
    return jsonify({
        "tcp": {
            "host": VISCA_IP_HOST,
            "port": VISCA_TCP_PORT,
            "clients": tcp_stats['clients'],
            "total_connections": tcp_stats['total_conn'],
            "ip_to_rs232": tcp_stats['ip_to_rs232'],
            "rs232_to_ip": tcp_stats['rs232_to_ip'],
            "last_activity": tcp_stats['last_activity']
        },
        "udp": {
            "port": VISCA_UDP_PORT
        },
        "serial": {
            "port": SERIAL_PORT,
            "baudrate": SERIAL_BAUDRATE,
            "connected": transport.serial is not None and transport.serial.is_open
        }
    })


@app.route("/", methods=["GET"])
def index():
    """Einfache Status-Seite"""
    return f"""
    <html>
    <head><title>VISCA Bridge</title></head>
    <body>
        <h1>VISCA Bridge Running</h1>
        <h2>Configuration</h2>
        <ul>
            <li>VISCA TCP: {VISCA_IP_HOST}:{VISCA_TCP_PORT}</li>
            <li>VISCA UDP: {VISCA_IP_HOST}:{VISCA_UDP_PORT}</li>
            <li>Web API: Port {WEB_PORT}</li>
            <li>Serial: {SERIAL_PORT} @ {SERIAL_BAUDRATE} baud</li>
        </ul>
        <h2>API Endpoints</h2>
        <ul>
            <li>GET /api/stats - Server statistics</li>
            <li>POST /preset/advanced - Advanced preset control</li>
            <li>POST /preset/virtual/&lt;id&gt; - Virtual preset recall</li>
        </ul>
    </body>
    </html>
    """

