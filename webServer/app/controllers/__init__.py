from flask import Blueprint

main_bp = Blueprint('main', __name__)

from app.controllers import main_controllers
