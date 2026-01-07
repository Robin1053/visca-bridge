import serial
import time
import threading


class SerialViscaTransport:
    def __init__(self, port: str, baudrate: int = 9600):
        self.port_name = port
        self.baudrate = baudrate
        self.serial = None
        self.lock = threading.Lock()
        self.running = True

        self._connect()
        threading.Thread(target=self._watchdog, daemon=True).start()

    def _connect(self):
        while self.serial is None:
            try:
                self.serial = serial.Serial(
                    port=self.port_name,
                    baudrate=self.baudrate,
                    timeout=0.5,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE
                )
                print(f"[VISCA] Connected to {self.port_name}")
            except serial.SerialException:
                print("[VISCA] Waiting for serial device...")
                time.sleep(2)

    def _watchdog(self):
        while self.running:
            if self.serial is None or not self.serial.is_open:
                print("[VISCA] Reconnecting...")
                self.serial = None
                self._connect()
            time.sleep(3)

    def send(self, data: bytes):
        with self.lock:
            try:
                self.serial.write(data)
            except Exception:
                self.serial = None

    def close(self):
        self.running = False
        if self.serial:
            self.serial.close()
