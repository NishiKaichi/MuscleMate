from flask import Flask, redirect, render_template, request
from markupsafe import Markup
import os, time
app = Flask(__name__)

@app.route('/')
def login():
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')