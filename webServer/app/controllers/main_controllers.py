# from flask import render_template  #, redirect, url_for, request, g, current_app
# from flask_login import current_user, login_required
from flask import jsonify, render_template, request, redirect, url_for, Response
from webServer.app.controllers import main_bp
from webServer.app.controllers.liveCamera import *
from webServer.app import lc, pp
from webServer.app import app, allowed_file, cfg
from werkzeug.utils import secure_filename
import os, cv2, socket, io

vc = cv2.VideoCapture(0)

@main_bp.route('/index', methods=['GET'])
def index_GET():
    images = os.listdir(cfg["upload_folder"])
    return render_template("index.html", images = images)

def videoStream():
    while True:
        rval, frame = vc.read()
        cv2.imwrite("pic.jpg", frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open('pic.jpg', 'rb').read() + b'\r\n')

@main_bp.route('/video_feed')
def video_feed():
    return Response(videoStream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

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
                        "filename": filename})

@main_bp.route("/switchActiveImage/<filename>", methods=["POST"])
def switchActiveImage(filename):
    print("The server is now using ", filename)
    return jsonify({"success": True})

@main_bp.route("/activateButton/<button>", methods=["GET"])
def activateButton(button):
    print("Pressed ", button)
    return jsonify({"success": True})
