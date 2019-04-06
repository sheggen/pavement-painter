from PIL import Image
import numpy
import time, datetime
from PCA_9685 import PCA_9685
import OBD2
numpy.set_printoptions(threshold=numpy.nan)  # for printing array during testing


class PavementPainter():    
    def __init__(self):
        """
        Initializes a new Pavement Painter object and starts it painting.
        """
        self.num_solenoids = 16*3 #Set to the number of solenoids to fire
        self.solenoid_spacing = 9.525     # in millimeters (3/8" = 9.525 mm)
        self.car_speed = 0
        self.fire_duration = .5
        self.fire_rate = .5 # How long to keep the solenoid open
        self.raw_image = None
        self.img_file = "test_img.png"
        self.img_matrix = []
        self.PCAs = []

        # Begin the magic
        self.odb2 = OBD2()      # Connect to OBD sensor
        self.parse_image()      # Load image
        self.init_PCAs()        # Ready the PCAs

        # Let it rain
        while True:
            self.paint()
            self.adjust_speed(self.odb2.get_speed())

    def init_PCAs(self):
        """
        Connects to the PCAs

        :return: None
        """
        num_sols = self.num_solenoids
        addr = 0x40

        while num_sols > 0:
            
            self.PCAs.append(PCA_9685(16, addr))
            num_sols -= 16
            addr += 1
        
    def adjust_speed(self, speed):
        """
        Adjusts the speed attribute based on vehicle speed.

        :param speed: the speed of the vehicle in KPH, which will control painting rate
        :return: None
        """

        self.fire_duration = self.solenoid_spacing / (speed * 1000000 / 3600)
        print(self.fire_duration)

    def parse_image(self):
        """
        Reads in an arbitrary image file and converts it to a binary image.

        :return: None
        """
        try:
            self.raw_image = Image.open(self.img_file)
            # self.raw_image.show("Original image")
            new_height = int(self.num_solenoids *(self.raw_image.size[1]/self.raw_image.size[0]))
            self.raw_image = self.raw_image.resize((self.num_solenoids, new_height))
            # self.raw_image.show("Resized image based on number of solenoids")
            self.raw_image = self.raw_image.convert("L")
            # self.raw_image.show("Black and white image")
            self.raw_image = self.raw_image.point(lambda i: i > 128 and 255)    # Converts image to a binary image
            # self.raw_image.show("Binary image")
            print(numpy.array(self.raw_image))
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
                # Add solenoid to fire list
                fire_list.append(counter % self.num_solenoids)
            else:
                # Stop solenoid if it's not being fired
                self.stop_fire(counter % self.num_solenoids)      # will this slow it down? should we make a stop list?
            counter += 1
            if counter == self.num_solenoids:
                self.adjust_speed()
                # st = datetime.datetime.now()
                for solenoid in fire_list:
                    self.fire(solenoid)
                # time.sleep(self.fire_rate)
                # for solenoid in fire_list:
                #     self.stop_fire(solenoid)
                time.sleep(self.fire_duration)
                # print("Took ", datetime.datetime.now() - st, " seconds to fire ", self.num_solenoids, " solenoids")
                counter = 0
                fire_list = []
                #print("--------------------------------------")

    def fire(self, solenoid):
        """
        Fire the solenoid for the correct amount of time, based on self.fire_rate

        :param solenoid: solenoid address
        :return: None
        """
        #print("Firing PCA: ", solenoid//16, ", Solenoid: ", solenoid % 16)
        self.PCAs[solenoid//16].fire_away(solenoid % 16)   # Picks the right PCA, then fires the right solenoid
        
    def stop_fire(self, solenoid):
        self.PCAs[solenoid//16].seize_fire(solenoid % 16)


PavementPainter()
