from flask import Flask, render_template
from extremes import fetch_extremes

app = Flask(__name__)

@app.route("/")
def index():
    cold, hot = fetch_extremes()
    # pass them straight into the template
    return render_template("index.html", cold=cold, hot=hot)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
