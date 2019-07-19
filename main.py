from flask import Flask, render_template, request, jsonify

import poof
import time

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about/')
def about():
    return render_template("about.html")


@app.route('/spoof', methods=['POST'])
def spoof():
    print("spoof")
    username = request.form['username']
    password = request.form['password']
    latitude = request.form["latitude"]
    longitude = request.form["longitude"]
    duration = request.form["duration"]
    timepassed = 0
    while timepassed < duration:
        poof.poof(username, password,
                  latitude, longitude)
        time.sleep(1)
        timepassed += 1
    return jsonify({'username': username,
                    "password": password,
                    "latitude": latitude,
                    "longitude": longitude,
                    "duration": duration
                    })


if __name__ == '__main__':
    app.run(debug=True)
