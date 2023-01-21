import os
import psycopg2
from flask import Flask

app = Flask(__name__)
conn = psycopg2.connect(os.environ["DATABASE_URL"])

@app.route("/sign_in")
def sign_in():
    pass

@app.route("/sign_up")
def sign_up():
    pass

@app.route("/analyze_audio", methods = ["POST"])
def analyze_audio():
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0")