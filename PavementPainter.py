from PIL import Image
import numpy
import time, datetime
from PCA_9685 import PCA_9685
from OBD2 import *
import threading
import RPi.GPIO as GPIO
import sys
numpy.set_printoptions(threshold=sys.maxsize)  # for printing array during testing


class PavementPainter(threading.Thread):    
    def __init__(self, threadID, camera):
        """
        Initializes a new Pavement Painter object and starts it painting.
        """
        self.num_solenoids = 45 #Set to the number of solenoids to fire
        self.solenoid_spacing = 9.525     # in millimeters (3/8" = 9.525 mm)
        self.scale_factor = 1000000      # 1000000 would print "to scale"
        self.car_speed = 0.01
        self.fire_duration = .01
        self.fire_rate = .01 # How long to keep the solenoid open #NO LONGER USED
        self.fire_percentage = .3# What percentage of time to fire/stop firing
        self.raw_image = None
        self.img_dict = {}
        #self.img_file = "WAVEY_LINES.jpg"
        #self.img_file = "Dandelion.jpg"
        #self.img_file = "IMAGE.jpg"
        self.img_file = "pigeon2.jpg"
        self.img_file = "passpig2j.jpg"
        self.img_file = "American_Chestnut4.jpg"
        self.img_file = "pigeon_flapping11.jpg"
        #self.img_file = "bird_pom_45X.jpg"

        #self.img_file = "Brook_trout_template45.jpg"
        self.img_file = "pigeon_flapping12.jpg"

        
        self.img_matrix = []
        self.PCAs = []
        
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
        
        # Access the camera object to update speed on live display
        self.camera = camera
        

    def run(self):
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
        print("Stopping print")
    
    def init_solenoids(self):
        self.stop_all()
        # input("Press any key to begin")
        print("Firing all to test")
        for i in range(self.num_solenoids):
            self.fire(i)
            time.sleep(1)        
            self.stop_fire(i)
        print("Test complete")
        
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
            new_height = int(self.num_solenoids *(self.raw_image.size[1]/self.raw_image.size[0]))
            self.raw_image = self.raw_image.resize((self.num_solenoids, new_height))  
            # self.raw_image.show("Resized image based on number of solenoids")
            self.raw_image = self.raw_image.convert("L")
            # self.raw_image.show("Black and white image")
            self.raw_image = self.raw_image.point(lambda i: i > 128 and 255)    # Converts image to a binary image
            # self.raw_image.show("Binary image")
            print(numpy.array(self.raw_image))

            # Construct a sparse dictionary representing image
            self.createSparseDict()

        except Exception as e:
            print(e)

    def createSparseDict(self):
        # Construct a sparse dictionary representing image
        row_counter = 0
        col_counter = 0
        for pixel in numpy.nditer(numpy.array(self.raw_image)):
            if pixel == 0:
                print(row_counter, " ", col_counter)
                self.img_dict[row_counter][col_counter] = 1
                print(self.img_dict)
            col_counter += 1
            if col_counter == self.num_solenoids:
                print("New row")
                row_counter += 1
                col_counter = 0
        #print(self.img_dict)


    def paint(self):
        """
        Fires solenoids based on binary image.

        :return: None
        """

        counter = 0
        fire_list = []

        st = time.time()    
        for pixel in numpy.nditer(numpy.array(self.raw_image)):
            
            if GPIO.input(self.speed_up_button):
                self.scale_factor += 10
                print("Speed up: ", self.scale_factor)
            if GPIO.input(self.speed_down_button):
                self.scale_factor -= 10
                print("Speed down: ", self.scale_factor)
            if pixel == 0:   # 0 for negative space; 255 for positive space
                # Add solenoid to fire list
                fire_list.append(counter % self.num_solenoids)
            #else:
                # Stop solenoid if it's not being fired
            #    self.stop_fire(counter % self.num_solenoids)      # will this slow it down? should we make a stop list?
            counter += 1
            if counter == self.num_solenoids:
                
                #print(fire_list)
                new_speed = self.obd2.get_speed()
                #print("Speed in main from obd: ", new_speed)
                if new_speed:
                    self.camera.camera.annotate_text = "{} KPH/{:0.2f} MPH".format(new_speed,
                                                                 new_speed/0.621371)
                    # self.camera.camera.annotate_background = picamera.color.Color('#000')

                    self.adjust_speed(new_speed)
                #st = datetime.datetime.now()
                #if new_speed > 8:
                for solenoid in fire_list:
                    self.fire(solenoid)
                time.sleep(self.fire_duration*self.fire_percentage)
                for solenoid in fire_list:
                   self.stop_fire(solenoid)
                    # print("Waiting: ", self.fire_duration)
                time.sleep(self.fire_duration*(1-self.fire_percentage))
                #print("Took ", datetime.datetime.now() - st, " seconds to fire ", self.num_solenoids, " solenoids")
                counter = 0
                fire_list = []
                #print("--------------------------------------")
        print("Paint time:", time.time() - st)

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

