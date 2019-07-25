from flask import Blueprint

main_bp = Blueprint('main', __name__)

from webServer.app.controllers import main_controllers
