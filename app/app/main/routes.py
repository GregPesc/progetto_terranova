from flask import Blueprint, render_template, send_file

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("index.html", title="Applicazione")


@main.route("/manifest.json")
def serve_manifest():
    return send_file("manifest.json", mimetype="application/manifest+json")


@main.route("/sw.js")
def serve_sw():
    return send_file("sw.js", mimetype="application/javascript")
