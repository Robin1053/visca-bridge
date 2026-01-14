import socket
import threading
import logging

log = logging.getLogger("visca-udp")


class ViscaUDPServer(threading.Thread):
    def __init__(self, transport, port=1259, sony_udp=True):
        super().__init__(daemon=True)
        self.transport = transport
        self.port = port
        self.sony_udp = sony_udp
        self.running = True

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", self.port))

        log.info(f"[UDP] VISCA UDP listening on :{self.port}")

    def run(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                log.debug(f"[UDP] {addr} -> {data.hex()}")

                # Sony VISCA-UDP Header (8 Byte) entfernen
                if self.sony_udp and len(data) > 8 and data[0] == 0x01 and data[1] == 0x00:
                    data = data[8:]
                    log.debug("[UDP] Sony header stripped")

                # an RS232 weiterleiten
                self.transport.send(data)

            except Exception as e:
                log.error(f"[UDP] error: {e}")

    def stop(self):
        self.running = False
        self.sock.close()
