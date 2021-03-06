# from flask import render_template  #, redirect, url_for, request, g, current_app
# from flask_login import current_user, login_required
from flask import jsonify, render_template, request, redirect, url_for, Response
from app.controllers import main_bp
# from app.controllers.liveCamera import *
import os
from app import cfg, allowed_file, pp 
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

@main_bp.route("/currentSpeed", methods=['GET'])
def currentSpeed():
    # print("Returning speeds")
    return str(pp.obd2.get_speed()) + " " + str(pp.scale_factor)


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
    pp.img_file = filename
    pp.parse_image()
    return jsonify({"success": True})

@main_bp.route("/activateButton/<button>/<state>", methods=["GET"])
def activateButton(button, state):
    print("Pressed ", button, state)
    if button == "startStopPrint":
        pp.amIPrinting = True if state == "True" else False
    if button == "motorUp":
        pp.amIMotorUp = True if state == "True" else False
    if button == "motorDown":
        pp.amIMotorDown = True if state == "True" else False
    if button == "speedUp":
        pp.amISpeedUp = True if state == "True" else False
    if button == "speedDown":
        pp.amISpeedDown = True if state == "True" else False
    if button == "flush":
        pp.amIFlushing = True if state == "True" else False

    return jsonify({"success": True})
