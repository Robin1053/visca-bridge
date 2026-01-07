from flask import Flask, request, jsonify
from serial_transport import SerialViscaTransport
from visca_presets import ViscaPresetsCV620

app = Flask(__name__)

transport = SerialViscaTransport("/dev/ttyUSB0")
presets = ViscaPresetsCV620(transport)


@app.route("/preset/advanced", methods=["POST"])
def preset_advanced():
    data = request.json
    presets.recall_advanced(data)
    return jsonify({"status": "ok"})


@app.route("/preset/virtual/<int:preset_id>", methods=["POST"])
def preset_virtual(preset_id):
    presets.recall_virtual(preset_id)
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
