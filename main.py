# TODO: Integrate with the PI, which consists of:
    # TODO: Add a start button to call paint()
    # TODO: Talk to the hardware through I2C
    # TODO: Dynamically handle addressing each solenoid through I2C
    # TODO: Handle addressing any number of solenoids with any number of port adapters
    # TODO: Convert fire() function to actually fire solenoid
    # TODO: Control self.speed attribute through OBDII connected to Pi

from PIL import Image
import numpy
import time
from PCA_9685 import PCA_9685
numpy.set_printoptions(threshold=numpy.nan)  # for printing array during testing


class PavementPainter():    
    def __init__(self):
        """
        Initializes a new Pavement Painter object and starts it painting.
        """
        self.num_solenoids = 25 #Set to the number of solenoids to fire
        self.speed = 3 # TODO: Control externally by speed of vehicle
        self.fire_rate = 1 # How long to keep the solenoid open
        self.raw_image = None
        self.img_file = "test_img.png"
        self.img_matrix = []
        self.PCAs = []
        
        self.parse_image()
        self.init_PCAs()
        self.paint()
        
        

    def init_PCAs(self):
        """
        Sets up correct number of PCAs, assumes ordered addressing starting at 0x40
        and goes up by 1 for each additional PCA.

        :return: None
        """
        num_PCAs = self.num_solenoids // 16
        last_PCA_num_solenoids = self.num_solenoids % 16
        
        for i in range(num_PCAs):
            self.PCAs.append(PCA_9685(16, 0x40+i))      # Auto add 1 for each PCA
        if last_PCA_num_solenoids:
            self.PCAs.append(PCA_9685(last_PCA_num_solenoids, 0x40+i))
        
        
    def adjust_speed(self, speed):
        """
        Adjusts the speed attribute based on vehicle speed. Thread?

        :param speed: the speed of the vehicle, which will control painting rate
        :return: None
        """

        self.speed = speed


    def parse_image(self):
        """
        Reads in an arbitrary image file and converts it to a binary image.

        :return: None
        """
        try:
            self.raw_image = Image.open(self.img_file)
            # self.raw_image.show("Original image")
            self.raw_image = self.raw_image.resize((self.num_solenoids, int(self.raw_image.size[1]/self.num_solenoids)))
            # self.raw_image.show("Resized image based on number of solenoids")
            self.raw_image = self.raw_image.convert("L")
            # self.raw_image.show("Black and white image")
            self.raw_image = self.raw_image.point(lambda i: i > 128 and 255)    # Converts image to a binary image
            self.raw_image.show("Binary image")
            # print(numpy.array(self.raw_image))
        except Exception as e:
            print(e)


    def paint(self):
        """
        Fires solenoids based on binary image.

        :return: None
        """

        counter = 0
        fire_list = []
        # TODO Run infinitely
        # FIXME: This is not doing what you think it's doing
        for pixel in numpy.nditer(numpy.array(self.raw_image)):
            if pixel == 255:   # 0 for negative space; 255 for positive space
                self.fire(counter%self.num_solenoids)
                fire_list.append(counter%self.num_solenoids)
            counter += 1
            if counter == self.num_solenoids:
                time.sleep(self.fire_rate)      # TODO: How do we handle stopping?
                counter = 0
                # print("--------------------------")
                # print(fire_list)                
                # print("--------------------------")

                for solenoid in fire_list:
                    self.PCAs[solenoid//16].seize_fire(solenoid % 16)
                time.sleep(self.speed)      # TODO: How do we handle stopping?
                fire_list = []
                print("------------------------------------------")

    def fire(self, solenoid):
        """
        Fire the solenoid for the correct amount of time, based on self.fire_rate

        :param solenoid: solenoid address
        :return: None
        """

        pca = solenoid//66
        solenoid_in_pca = solenoid % 16
        print("Firing PCA: ", pca , ", Solenoid: ", solenoid_in_pca )
        self.PCAs[pca].fire_away(solenoid_in_pca)   # Picks the right PCA, then fires the right solenoid
        

PavementPainter()   # GO!
