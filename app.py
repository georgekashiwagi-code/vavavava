from flask import Flask,request
import threading,os

app=Flask(__name__)
TOKEN="MY_WC_SECRET_928371"
messages=[]
lock=threading.Lock()
next_id=1

@app.route("/")
def home():
    return "WC Chat Server OK"

@app.route("/send")
def send():
    global next_id

    if request.args.get("token")!=TOKEN:
        return "ERR",403

    name=request.args.get("name","")[:32]
    pid=request.args.get("player_id","")[:5]
    client=request.args.get("client","")[:64]
    msg=request.args.get("message","")[:200]

    if not name or not msg:
        return "ERR",400

    with lock:
        item={
            "id":next_id,
            "name":name,
            "pid":pid,
            "client":client,
            "msg":msg
        }
        messages.append(item)
        current=next_id
        next_id+=1

        if len(messages)>100:
            del messages[:-100]

    return "OK|"+str(current)

@app.route("/poll")
def poll():
    if request.args.get("token")!=TOKEN:
        return "ERR",403

    try:
        after=int(request.args.get("after","0"))
    except:
        after=0

    with lock:
        result=[x for x in messages if x["id"]>after]

    return "\n".join(
        "{}|{}|{}|{}|{}".format(
            x["id"],
            x["name"],
            x["pid"],
            x["client"],
            x["msg"]
        )
        for x in result
    )

@app.route("/latest")
def latest():
    if request.args.get("token")!=TOKEN:
        return "ERR",403

    with lock:
        return str(messages[-1]["id"] if messages else 0)

if __name__=="__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT",5000))
    )
