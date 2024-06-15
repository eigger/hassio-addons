from flask import Flask, request, jsonify
import led

app = Flask(__name__)

@app.route("/led", methods=["POST"])
def process_led():
    data = {"success": False}

    mode = request.json.get('mode', 0x04)
    brightness = request.json.get('brightness', 0x05)
    speed = request.json.get('speed', 0x05)

    try:
        led.control("/dev/ttyS2", 9600, mode, brightness, speed)
        data['success'] = True
    except Exception as e:
        return jsonify(data), 500

    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5090, debug=True)
