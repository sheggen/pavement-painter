from board import SCL, SDA
import busio
from Adafruit_CircuitPython_PCA9685.adafruit_pca9685 import PCA9685
import time

class PCA_9685():
    def __init__(self, num_solenoids, addr):
        """
        Creates a new PCA object

        :param num_solenoids: number of solenoids that are connected to this PCA
        :param addr: the I2C address of the PCA
        """
        self.i2c_bus = busio.I2C(SCL, SDA)
        try:
            self.pca = PCA9685(self.i2c_bus, address = addr)
            print("PCA found on: ", addr)
        except:
            print("Failed to initialize PCA on address: ", addr)
        self.pca.frequency = 1500
        self.num_solenoids = num_solenoids


    def fire_away(self, solenoid):
        """
        Activates the solenoid.

        :param solenoid: channel of the solenoid
        :return:  None
        """
        # The PCA9685 object has a channels attribute which has an object for each channel
        solenoid_channel = self.pca.channels[solenoid]
        solenoid_channel.duty_cycle = 0xffff  # fire solenoid
      
    def seize_fire(self, solenoid):
        """
        Deactivate the solenoid.

        :param solenoid: channel of the solenoid
        :return: None
        """
        solenoid_channel = self.pca.channels[solenoid]
        solenoid_channel.duty_cycle = 0x0000  # unfire solenoid


    def reset(self):
        self.pca.reset()

if __name__ == "__main__":
    x = PCA_9685(16, 0x40)
    
    while True:
        pass
        x.fire_away(3)
