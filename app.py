from flask import Flask, request
import threading
import os

app=Flask(__name__)
TOKEN="MY_WC_SECRET_928371"
messages=[]
lock=threading.Lock()
next_id=1
MAX_MESSAGES=100

@app.route("/")
def home():
    return "WC Chat Server OK"

@app.route("/send")
def send():
    global next_id
    if request.args.get("token","")!=TOKEN:return "ERR",403

    name=request.args.get("name","")[:32].replace("|","")
    pid=request.args.get("player_id","")[:5].replace("|","")
    msg=request.args.get("message","")[:200].replace("|","/").replace("\n"," ").replace("\r"," ")
    client=request.args.get("client","")[:32].replace("|","")

    if not name or not msg:return "ERR",400

    with lock:
        item={"id":next_id,"name":name,"player_id":pid,"message":msg,"client":client}
        messages.append(item)
        n=next_id
        next_id+=1
        if len(messages)>MAX_MESSAGES:del messages[:-MAX_MESSAGES]

    return "OK|"+str(n)

@app.route("/poll")
def poll():
    if request.args.get("token","")!=TOKEN:return "ERR",403
    try:after=int(request.args.get("after","0"))
    except:after=0

    with lock:
        r=[m for m in messages if m["id"]>after]

    return "\n".join(
        "{}|{}|{}|{}|{}".format(
            m["id"],m["name"],m["player_id"],m["client"],m["message"]
        ) for m in r
    )

@app.route("/latest")
def latest():
    if request.args.get("token","")!=TOKEN:return "ERR",403
    with lock:return str(messages[-1]["id"] if messages else 0)

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))
