from flask import Flask
app = Flask(__name__)

@app.route("/") #当然ここでの app は2行目の app を受けて。2行目が hoge = Flask... であれば @hoge.route(...) とする。
def hello_world():
    return"<p>Hello World!</p>"

@app.route("/about")
def about():
    return "leviatan"