
from flask import Flask
import yaml
from flask_bootstrap import Bootstrap
import os

app = Flask(__name__)
bootstrap = Bootstrap(app)
def load_config(file):
    with open(file, 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
    #    print("cfg", cfg)
    return cfg

def check_folder_existance(filepath):
    if not os.path.exists(filepath):
        os.makedirs(filepath)

cfg = load_config("app/config/secret_config.yaml")
app.secret_key = cfg["secret_key"]

check_folder_existance(cfg["upload_folder"])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in cfg['allowed_extensions']

from app.PavementPainter import PavementPainter
#from app.controllers.liveCamera import LiveCamera

# Create a camera object
#lc = LiveCamera(2)

# Create a PavementPainter object
pp = PavementPainter(1)

# Run them both on their own threads
pp.start()
# lc.start()

# Registers blueprints (controllers). These are general routes, like /index
from app.controllers import main_bp as main_bp
app.register_blueprint(main_bp)
