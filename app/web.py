from flask import Flask, render_template

app = Flask(__name__)


@app.get("/")
def index():
    return "Hyde Park and the Legalizers — coming soon"


@app.get("/epk")
def epk():
    return render_template("epk.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
