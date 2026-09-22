from flask import Flask, request
import threading
import os

app = Flask(__name__)

TOKEN = "MY_WC_SECRET_928371"
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

    name = name.replace("|", "")
    player_id = player_id.replace("|", "")
    message = message.replace("|", "/").replace("\n", " ").replace("\r", " ")

    with lock:
        item = {
            "id": next_id,
            "name": name,
            "player_id": player_id,
            "message": message
        }

        messages.append(item)
        current_id = next_id
        next_id += 1

        if len(messages) > MAX_MESSAGES:
            del messages[:-MAX_MESSAGES]

    return "OK|" + str(current_id)

@app.route("/poll")
def poll():
    if request.args.get("token", "") != TOKEN:
        return "ERR", 403

    try:
        after = int(request.args.get("after", "0"))
    except:
        after = 0

    with lock:
        result = [m for m in messages if m["id"] > after]

    return "\n".join(
        "{}|{}|{}|{}".format(
            m["id"],
            m["name"],
            m["player_id"],
            m["message"]
        )
        for m in result
    )

@app.route("/latest")
def latest():
    if request.args.get("token", "") != TOKEN:
        return "ERR", 403

    with lock:
        return str(messages[-1]["id"] if messages else 0)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
