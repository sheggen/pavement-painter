from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
import time

class PCA_9685():
    def __init__(self, num_solenoids, addr):        
        self.i2c_bus = busio.I2C(SCL, SDA)
        try:
            self.pca = PCA9685(self.i2c_bus, address = addr)
        except:
            print("Failed to initialize PCA on address: ", addr)
        self.pca.frequency = 25 # Can be used to easily control on/off time of Solenoid!
        self.num_solenoids = num_solenoids


    def fire_away(self, solenoid):
        # The PCA9685 object has a channels attribute which has an object for each channel
        solenoid_channel = self.pca.channels[solenoid]
        solenoid_channel.duty_cycle = 0xffff  # fire solenoid
      
    def seize_fire(self, solenoid):
        solenoid_channel = self.pca.channels[solenoid]
        solenoid_channel.duty_cycle = 0x0000  # fire solenoid

if __name__ == "__main__":
    x = PCA_9685(16)
    x.fire_away(11)