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

class PavementPainter():
    def __init__(self):
        """
        Initializes a new Pavement Painter object and starts it painting.
        """
        self.num_solenoids = 250 #Set to the number of solenoids to fire
        self.speed = 2 # TODO: Control externally by speed of vehicle
        self.fire_rate = 10 # How long to keep the solenoid open
        self.raw_image = None
        self.img_file = "test_img.jpg"
        self.img_matrix = []
        self.parse_image()
        self.paint()

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
            self.raw_image = self.raw_image.convert("L")
            # self.raw_image.show("Black and white image")
            self.raw_image = self.raw_image.resize((int(self.raw_image.size[1]/self.num_solenoids), self.num_solenoids))
            # self.raw_image.show("Resized image based on number of solenoids")
            self.raw_image = self.raw_image.point(lambda i: i > 128 and 255)
            # self.raw_image.show("Binary image")
            # print(self.img_matrix)
            # print(self.raw_image)
        except Exception as e:
            print(e)


    def paint(self):
        """
        Fires solenoids based on binary image.

        :return: None
        """

        counter = 0
        # TODO Run infinitely
        for pixel in numpy.nditer(numpy.array(self.raw_image)):
            if pixel == 255:
                self.fire(counter%self.num_solenoids)
            counter += 1
            if counter == self.num_solenoids - 1:
                time.sleep(self.speed)      # TODO: How do we handle stopping?
                counter = 0

    def fire(self, solenoid):
        """
        Fire the solenoid for the correct amount of time, based on self.fire_rate

        :param solenoid: solenoid address
        :return: None
        """
        print("Firing ", solenoid)

PavementPainter()
