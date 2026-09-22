from flask import Flask, request
import threading
import time
import os

app = Flask(__name__)

TOKEN = "CHANGE_THIS_SECRET"
messages = []
lock = threading.Lock()
next_id = 1
MAX_MESSAGES = 100

@app.route("/")
def home():
    return "WC Chat Server OK"

@app.route("/send", methods=["POST"])
def send():
    global next_id

    if request.form.get("token", "") != TOKEN:
        return "ERR", 403

    name = str(request.form.get("name", ""))[:32]
    player_id = str(request.form.get("player_id", ""))[:5]
    message = str(request.form.get("message", ""))[:200]

    if not name or not message:
        return "ERR", 400

    with lock:
        item = {
            "id": next_id,
            "name": name,
            "player_id": player_id,
            "message": message,
            "time": int(time.time())
        }

        messages.append(item)
        current_id = next_id
        next_id += 1

        if len(messages) > MAX_MESSAGES:
            del messages[:-MAX_MESSAGES]

    return "OK|" + str(current_id)

@app.route("/poll", methods=["GET"])
def poll():
    if request.args.get("token", "") != TOKEN:
        return "ERR", 403

    try:
        after = int(request.args.get("after", "0"))
    except:
        after = 0

    with lock:
        result = [m for m in messages if m["id"] > after]

    lines = []

    for m in result:
        name = m["name"].replace("|", "")
        player_id = m["player_id"].replace("|", "")
        message = m["message"].replace("|", "/").replace("\n", " ")

        lines.append(
            "{}|{}|{}|{}".format(
                m["id"],
                name,
                player_id,
                message
            )
        )

    return "\n".join(lines)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
