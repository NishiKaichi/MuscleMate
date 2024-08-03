from flask import Flask             #Flaskクラスのインポート

app=Flask(__name__)                 #Flaskクラスのインスタンスを作成

@app.route("/")                     #routeデコレータを使ってどのURLが関数の引き金になるのかを伝える
def hello_world():                  
    return "<p>tsttststststststsaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa</p>"