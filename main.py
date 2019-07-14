from flask import Flask, render_template, request, jsonify

import poof

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('form.html')


@app.route('/spoof', methods=['POST'])
def spoof():
    username = request.form['username']
    password = request.form['password']
    poof.poof(username, password)
    return jsonify({'username': username,
                    "password": password})


if __name__ == '__main__':
    app.run(debug=True)
