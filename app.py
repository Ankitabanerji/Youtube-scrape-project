import os
import json
import time
import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
from data_scrapp import scrape_youtube_data
from flask import jsonify, request
from flask_executor import Executor
from upload_monodb_snowflake_gdrive import upload_operations

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
executor = Executor(app)
app.config['EXECUTOR_TYPE'] = 'thread'
app.config['EXECUTOR_MAX_WORKERS'] = 5


@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homepage():
    return render_template("index.html")


@app.route('/loading', methods=['POST', 'GET'])  # route to show loading page
@cross_origin()
def index():
    if request.method == 'POST':
        channel_link = request.form['channel_link']

        # Flask-Executor is a Flask extension that makes it easy to work with concurrent.futures in your application.
        executor.submit(scrape_youtube_data, channel_link)

        return render_template('loading.html')


@app.route('/get_video_data', methods=['POST'])
@cross_origin()
def get_data():
    file_path = 'resources/data.json'
    if os.path.isfile(file_path):
        return jsonify({"status": True})
    else:
        return jsonify({"status": False})


@app.route('/show_result') # route to show results table
@cross_origin()
def show_data():
    file_path = 'resources/data.json'
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read()
    time.sleep(2)
    if os.path.isfile(file_path):
        os.remove(file_path)

    executor.submit(upload_operations, json.loads(data))

    return render_template('results.html', results_data=json.loads(data)["data"])


if __name__ == '__main__':
    app.run(debug=True)
