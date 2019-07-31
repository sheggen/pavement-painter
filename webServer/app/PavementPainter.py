from PIL import Image
import numpy
import time, datetime
from app.PCA_9685 import PCA_9685
from app.OBD2 import *
import threading
import RPi.GPIO as GPIO
import sys
numpy.set_printoptions(threshold=sys.maxsize)  # for printing array during testing


class PavementPainter(threading.Thread):    
    def __init__(self, threadID):
        """
        Initializes a new Pavement Painter object and starts it painting.
        """
        self.num_solenoids = 12 #Set to the number of solenoids to fire
        self.solenoid_spacing = 9.525     # in millimeters (3/8" = 9.525 mm)
        self.scale_factor = 1000000      # 1000000 would print "to scale"
        self.car_speed = 0.01
        self.fire_duration = .01
        self.fire_rate = .01 # How long to keep the solenoid open #NO LONGER USED
        self.fire_percentage = .3# What percentage of time to fire/stop firing
        self.raw_image = None
        self.img_dict = {}
        self.img_file = "static/images/Dandelion.jpg"
        self.new_height = 0         # Height of the image after resizing
        self.img_matrix = []
        self.PCAs = []

        # States for web server
        self.amIPrinting = False
        self.amIMotorUp = False
        self.amIMotorDown = False
        self.amISpeedUp = False
        self.amISpeedDown = False
        self.amIFlushing = False

        # GPIO pins
        self.initialize_solenoids_button = 13        
        self.start_button = 19
        self.stop_button = 26
        self.lift_up_button = 12
        self.lift_down_button = 6
        self.speed_up_button = 23
        self.speed_down_button = 24
        
        self.dir_L = 16
        self.dir_R = 20
        #self.enable_lift = 21

        # Begin the magic
        self.init_GPIO()
        self.obd2 = OBD2()      # Connect to OBD sensor
        self.parse_image()      # Load image
        self.init_PCAs()        # Ready the PCAs
        
        # self.init_solenoids()
        self.last_button_state = 0   # 0 = not firing, 1 = firing
        
        # For threading with the live feed camera
        threading.Thread.__init__(self)
        self.threadID = threadID
        
    def run(self):     # webServerRun       # Switch function name to run(self): to use webserver instead of buttons
        print("Rain started")
        while True:
            self.init_GPIO_2()  # Resets GPIOs since they are cleaned out each loop iteration

            # Paint if button was pressed once
            if self.amIPrinting:
                self.paint()
            else:
                self.stop_all()

            # Move the motors up/down
            if self.amIMotorUp:
                print("Motor up started")
                GPIO.output(self.dir_L, GPIO.HIGH)
                GPIO.output(self.dir_R, GPIO.LOW)
            if self.amIMotorDown:
                print("Motor Down started")
                GPIO.output(self.dir_R, GPIO.HIGH)
                GPIO.output(self.dir_L, GPIO.LOW)
            
            # Adjust the speed up/down
            if self.amISpeedUp:
                print("Speed up")
                self.scale_factor += 100
            if self.amISpeedDown:
                print("Speed down")
                self.scale_factor -= 100

            # Flush the solenoids
            if self.amIFlushing:
                self.init_solenoids()
            GPIO.cleanup()


    def GPIOrun(self):          # Switch function name to run(self): to use buttons instead of webserver
        # Let it rain
        print("Rain started")
        while True:
            self.init_GPIO()  # Resets GPIOs since they are cleaned out each loop iteration
            # Lift up/down buttons
            while GPIO.input(self.lift_up_button):
                #print("Going up?")
                #GPIO.output(self.enable_lift, GPIO.HIGH)
                GPIO.output(self.dir_L, GPIO.HIGH)
                GPIO.output(self.dir_R, GPIO.LOW)
            while GPIO.input(self.lift_down_button):
                #print("Going down?")
                #GPIO.output(self.enable_lift, GPIO.HIGH)
                GPIO.output(self.dir_R, GPIO.HIGH)
                GPIO.output(self.dir_L, GPIO.LOW)
            # print("Stopping lift")
            GPIO.output(self.dir_R, GPIO.LOW)
            GPIO.output(self.dir_L, GPIO.LOW)
            
            # Start, Stop, and Initialize buttons
            if GPIO.input(self.initialize_solenoids_button): # Initialize solenoids
                self.init_solenoids()
            if GPIO.input(self.stop_button):   # Stop all solenoids
                self.last_button_state = 0
                self.stop_all()
            if not GPIO.input(self.initialize_solenoids_button) and not GPIO.input(self.stop_button) and not GPIO.input(self.start_button):  # keep firing if already firing
                if self.last_button_state:
                    self.paint()
            if GPIO.input(self.start_button):   # Start all solenoids
                print("Starting print")
                self.last_button_state = 1 
                self.paint()
            
            # Speed adjust buttons
            if not self.last_button_state:
                if GPIO.input(self.speed_up_button):
                    self.scale_factor += 100
                    print("Speed up: ", self.scale_factor)
                if GPIO.input(self.speed_down_button):
                    self.scale_factor -= 100
                    print("Speed down: ", self.scale_factor)
            GPIO.cleanup()


    def init_GPIO_2(self):
        GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
        GPIO.setup(self.dir_L, GPIO.OUT)
        GPIO.setup(self.dir_R, GPIO.OUT)


    def init_GPIO(self):
        
        GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
        
        #GPIO.setup(18, GPIO.OUT)   # Using 18 as power # DID You stop doing this?
        #GPIO.output(18, GPIO.HIGH)  # Did you stop doing this?
        GPIO.setup(self.initialize_solenoids_button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.start_button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Button pin set as input w/ pull-up
        GPIO.setup(self.stop_button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Button pin set as input w/ pull-up
        
        #GPIO.setup(self.enable_lift, GPIO.OUT)
        GPIO.setup(self.dir_L, GPIO.OUT)
        GPIO.setup(self.dir_R, GPIO.OUT)
        GPIO.setup(self.lift_up_button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Button pin set as input w/ pull-up
        GPIO.setup(self.lift_down_button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Button pin set as input w/ pull-up
        GPIO.setup(self.speed_up_button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.speed_down_button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

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
    
    def stop_all(self):
        for i in range(self.num_solenoids):
            self.stop_fire(i)
            #time.sleep(.01)
        # print("Stopping print")
    
    def init_solenoids(self):
        self.stop_all()
        # input("Press any key to begin")
        #print("Firing all to test")
        for i in range(self.num_solenoids):
            self.fire(i)
            time.sleep(1)        
            self.stop_fire(i)
        #print("Test complete")
        
    def adjust_speed(self, speed):
        """
        Adjusts the speed attribute based on vehicle speed.

        :param speed: the speed of the vehicle in KPH, which will control painting rate
        :return: None
        """

        self.fire_duration = self.solenoid_spacing / (speed * self.scale_factor / 3600)
        #print("Speed: ", speed, ", Fire duration: ", self.fire_duration)

    def parse_image(self):
        """
        Reads in an arbitrary image file and converts it to a binary image.

        :return: None
        """
        try:
            self.raw_image = Image.open(self.img_file)
            # self.raw_image.show("Original image")
            self.new_height = int(self.num_solenoids *(self.raw_image.size[1]/self.raw_image.size[0]))
            print(self.new_height)
            self.raw_image = self.raw_image.resize((self.num_solenoids, self.new_height))
            # self.raw_image.show("Resized image based on number of solenoids")
            self.raw_image = self.raw_image.convert("L")
            # self.raw_image.show("Black and white image")
            self.raw_image = self.raw_image.point(lambda i: i > 128 and 255)    # Converts image to a binary image
            # self.raw_image.show("Binary image")
            #print(numpy.array(self.raw_image))

            # Construct a sparse dictionary representing image
            self.createSparseDict()

        except Exception as e:
            print(e)

    def createSparseDict(self):
        # Construct a sparse dictionary representing image
        counter = 0
        for pixel in numpy.nditer(numpy.array(self.raw_image)):
            if pixel == 0:    
                self.img_dict[counter//self.num_solenoids] = self.img_dict.get(counter//self.num_solenoids, [])
                self.img_dict[counter//self.num_solenoids].append(counter%self.num_solenoids)
            counter += 1

    def paint(self):
        """
        Fires solenoids based on binary image.

        :return: None
        """
        new_speed = self.obd2.get_speed()
        if new_speed:
            #self.camera.camera.annotate_text = "{} KPH/{:0.2f} MPH".format(new_speed,
             #                                                              new_speed / 0.621371)
            self.adjust_speed(new_speed)

        st = time.time()

        # Paint from the list (slow)
        #self.paint_from_list()

        # Paint from the dictionary (faster?)
        self.paint_from_dict()

        # print("Paint time:", time.time() - st)

    def paint_from_dict(self):
        for i in range(self.new_height):             
            for k in self.img_dict.get(i, []):
                self.fire(k)
            # time.sleep((self.fire_duration * self.fire_percentage))

            self.reset()  # TODO Does this work?
            #for k in self.img_dict.get(i, []):
            #    self.stop_fire(k)
            # time.sleep((self.fire_duration * (1 - self.fire_percentage)))


    def paint_from_list(self):
        counter = 0
        fire_list = []
        for pixel in numpy.nditer(numpy.array(self.raw_image)):

            # TODO MOVE GPIO to own class.
            #if GPIO.input(self.speed_up_button):
            #    self.scale_factor += 10
            #    print("Speed up: ", self.scale_factor)
            #if GPIO.input(self.speed_down_button):
            #    self.scale_factor -= 10
            #    print("Speed down: ", self.scale_factor)
            if pixel == 0:  # 0 for negative space; 255 for positive space
                # Add solenoid to fire list
                fire_list.append(counter % self.num_solenoids)
            counter += 1
            if counter == self.num_solenoids:

                # Adjust speed
                new_speed = self.obd2.get_speed()
                # print("Speed in main from obd: ", new_speed)
                if new_speed:
             #       self.camera.camera.annotate_text = "{} KPH/{:0.2f} MPH".format(new_speed,
             #                                                                      new_speed / 0.621371)
                    self.adjust_speed(new_speed)

                # Fire solenoids
                for solenoid in fire_list:
                    self.fire(solenoid)
                # time.sleep((self.fire_duration * self.fire_percentage)/6)
                for solenoid in fire_list:
                    self.stop_fire(solenoid)
                    # print("Waiting: ", self.fire_duration)
                # time.sleep((self.fire_duration * (1 - self.fire_percentage))/6)

                counter = 0
                fire_list = []

    def fire(self, solenoid):
        """
        Fire the solenoid for the correct amount of time, based on self.fire_rate

        :param solenoid: solenoid address
        :return: None
        """
        # print("Firing PCA: ", solenoid//16, ", Solenoid: ", solenoid % 16)
        self.PCAs[solenoid//16].fire_away(solenoid % 16)   # Picks the right PCA, then fires the right solenoid
        
    def stop_fire(self, solenoid):
        self.PCAs[solenoid//16].seize_fire(solenoid % 16)

    def reset(self):
        for pca in self.PCAs:
            pca.reset()
