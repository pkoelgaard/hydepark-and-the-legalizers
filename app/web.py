import json
from pathlib import Path
from flask import Flask, render_template
from merch import merch, shop_settings

app = Flask(__name__)
app.register_blueprint(merch)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
NAVIGATION = [('tour', 'Koncerter / Tour'), ('bio', 'Om bandet / Bio'), ('music', 'Musik / Diskografi'), ('contact', 'Kontakt / Booking'), ('epk', 'Pressekit / EPK'), ('gallery', 'Galleri / Video'), ('shop', 'Shop / Merch')]

@app.context_processor
def site_context():
    return {"navigation": NAVIGATION, "content": json.loads((Path(__file__).parent / "content.json").read_text())}

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/epk")
def epk():
    return render_template("epk.html")

@app.get("/tour")
def tour():
    return render_template("tour.html")

@app.get("/bio")
def bio():
    return render_template("bio.html")

@app.get("/music")
def music():
    return render_template("music.html")

@app.get("/contact")
def contact():
    return render_template("contact.html")

@app.get("/gallery")
def gallery():
    return render_template("gallery.html")

@app.get("/shop")
def shop():
    return render_template("shop.html", **shop_settings())

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
