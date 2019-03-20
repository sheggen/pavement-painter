from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685


class PCA_9685():
    def __init__(self):
        i2c_bus = busio.I2C(SCL, SDA)
        pca = PCA9685(i2c_bus)
        pca.frequency = 60 # Can be used to easily control on/off time of Solenoid!

        # The PCA9685 object has a channels attribute which has an object for each channel
        solenoid_channel = pca.channels[0]  # where stuff is connected

