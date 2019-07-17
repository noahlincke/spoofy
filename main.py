from flask import Flask, render_template, request, jsonify

import poof

from rq import Queue
from worker import conn

q = Queue(connection=conn)

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/spoof', methods=['POST'])
def spoof():
    print("spoof")
    username = request.form['username']
    password = request.form['password']
    latitude = request.form["latitude"]
    longitude = request.form["longitude"]
    duration = request.form["duration"]
    job = q.enqueue(poof.poof(username, password,
                              latitude, longitude, duration))
    return jsonify({'username': username,
                    "password": password,
                    "latitude": latitude,
                    "longitude": longitude,
                    "duration": duration
                    })


if __name__ == '__main__':
    app.run(debug=True)
