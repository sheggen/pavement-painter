# from flask import render_template  #, redirect, url_for, request, g, current_app
# from flask_login import current_user, login_required
from flask import jsonify, render_template, request, redirect, url_for
from app.controllers import main_bp
# from app.controllers.liveCamera import *
from app import app, allowed_file, cfg
from werkzeug.utils import secure_filename
import os

@main_bp.route('/index', methods=['GET'])
def index_GET():
    images = os.listdir(cfg["upload_folder"])

    return render_template("index.html", images = images)

@main_bp.route("/addImage", methods=["POST"])
def changeImage():
    data = request.files
    print(data)
    if 'inputImage' not in data:
        print("File not found")
        return redirect(url_for("main.index_GET"))
    file = data['inputImage']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        print("File unnamed")
        return redirect(url_for("main.index_GET"))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(cfg["upload_folder"], filename))

        return jsonify({"success": True,
                        "filename": file.filename})

@main_bp.route("/switchActiveImage/<filename>", methods=["POST"])
def switchActiveImage(filename):
    print("The server is now using ", filename)
    return jsonify({"success": True})
