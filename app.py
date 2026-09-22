from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

TOKEN = "CHANGE_THIS_SECRET"
messages = []
lock = threading.Lock()
next_id = 1
MAX_MESSAGES = 100

@app.get("/")
def home():
    return "WC Chat Server OK"

@app.post("/send")
def send():
    global next_id

    data = request.get_json(silent=True) or {}

    if data.get("token") != TOKEN:
        return jsonify({"ok": False}), 403

    name = str(data.get("name", ""))[:32]
    player_id = str(data.get("player_id", ""))[:5]
    message = str(data.get("message", ""))[:200]

    if not name or not message:
        return jsonify({"ok": False}), 400

    with lock:
        item = {
            "id": next_id,
            "name": name,
            "player_id": player_id,
            "message": message
        }

        messages.append(item)
        next_id += 1

        if len(messages) > MAX_MESSAGES:
            del messages[:-MAX_MESSAGES]

    return jsonify({"ok": True})

@app.get("/poll")
def poll():
    if request.args.get("token") != TOKEN:
        return jsonify({"ok": False}), 403

    try:
        after = int(request.args.get("after", 0))
    except:
        after = 0

    with lock:
        result = [m for m in messages if m["id"] > after]

    return jsonify({
        "ok": True,
        "messages": result
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
