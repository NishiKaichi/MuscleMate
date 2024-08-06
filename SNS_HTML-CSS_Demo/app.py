from flask import Flask, redirect, render_template, request
from markupsafe import Markup
import os, time
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login_form.html')



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')