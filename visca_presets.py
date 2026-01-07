import json
import os


class ViscaPresetsCV620:
    def __init__(self, transport, preset_file="presets.json"):
        self.transport = transport
        self.preset_file = preset_file
        self.virtual_presets = self._load_presets()

    # --------------------------------------------------
    # Low-Level
    # --------------------------------------------------

    def _send(self, data):
        self.transport.send(bytearray(data))

    # --------------------------------------------------
    # CV620 Controls
    # --------------------------------------------------

    def set_focus(self, mode: str):
        if mode == "auto":
            self._send([0x81, 0x01, 0x04, 0x38, 0x02, 0xFF])
        elif mode == "manual":
            self._send([0x81, 0x01, 0x04, 0x38, 0x03, 0xFF])

    def set_zoom_speed(self, speed: int):
        speed = max(0, min(7, speed))
        self._send([0x81, 0x01, 0x04, 0x07, 0x20 | speed, 0xFF])

    def set_pan_tilt_speed(self, pan: int, tilt: int):
        pan = max(1, min(0x18, pan))
        tilt = max(1, min(0x18, tilt))

        self._send([
            0x81, 0x01, 0x06, 0x01,
            pan, tilt,
            0x03, 0x03,
            0xFF
        ])

    # --------------------------------------------------
    # Hardware Presets
    # --------------------------------------------------

    def recall_preset(self, preset: int):
        self._send([
            0x81, 0x01, 0x04, 0x3F,
            0x02,
            preset - 1,
            0xFF
        ])

    def recall_advanced(self, data: dict):
        if "focus" in data:
            self.set_focus(data["focus"])

        if "zoom_speed" in data:
            self.set_zoom_speed(data["zoom_speed"])

        self.set_pan_tilt_speed(
            data.get("pan_speed", 6),
            data.get("tilt_speed", 6)
        )

        self.recall_preset(data["camera_preset"])

    # --------------------------------------------------
    # Virtual Presets
    # --------------------------------------------------

    def recall_virtual(self, preset_id: int):
        preset = self.virtual_presets.get(str(preset_id))
        if not preset:
            raise ValueError("Preset nicht gefunden")
        self.recall_advanced(preset)

    def _load_presets(self):
        if not os.path.exists(self.preset_file):
            return {}
        with open(self.preset_file, "r") as f:
            return json.load(f)
