import obd
import datetime, time

class OBD2():
    """
    Handles connection to the OBD2 sensor and returns data

    """
    def __init__(self):
        # obd.logger.setLevel(obd.logging.DEBUG)
        self.fake_speed = 80 # For testing only
        self.up = True       # For testing only
        
        try:
            self.connection = obd.Async()               # auto-connects to USB or RF port
            self.connection.watch(obd.commands.SPEED)       # Watch the speed value from OBD2
            self.connection.start()
            print("Successfully connected to car")

        except:
            try:
                # Try connecting a slightly less automatic way
                self.ports = obd.scan_serial()          # return list of valid USB or RF ports
                print (self.ports)                      # ['/dev/ttyUSB0', '/dev/ttyUSB1']
                self.connection = obd.Async(self.ports[0])  # connect to the first port in the list
                self.connection.watch(obd.commands.SPEED)       # Watch the speed value from OBD2
                self.connection.start()
                print("Successfully connected to car, attempt 2")
            except:
                print("No car found")
                #self.fake_it()
        

    def get_speed(self):
        """
        Returns the speed from the OBD2

        :return: speed of the vehicle in kmph
        """
        try:
            raw_speed = self.connection.query(obd.commands.SPEED)
            # print(str(raw_speed.value).split(" ")[0])
            raw_speed_2 = int(str(raw_speed.value).split(" ")[0])
            # print(raw_speed_2)
            if raw_speed_2:
                return raw_speed_2  # non-blocking, returns immediately
        except:
            print("Speed not found")
            # return self.fake_it()
            
            
            
    def fake_it(self):
        """
        Fake the speed for testing only.
        
        return: int between 5 - 100
        """
               
        if self.fake_speed == 85 or self.fake_speed == 75:
            self.up = not self.up
        if self.up:
            self.fake_speed += 1
        else:
            self.fake_speed -= 1
        return self.fake_speed
        
            
if __name__ == "__main__":
    """
    Writes speed, date, time, and conversion to shots per second to a file
    """
    o = OBD2()
    while True:
        f = open("logger.txt", "a")
        s = str(o.get_speed())
        t = str(datetime.datetime.now())
        # print("Speed: ", s)
        f.write(t + ", " + s + ", ")
        try:
            f.write(str(9.525/(int(s.split(" ")[0])*1000/3600)))
        except:
            pass
        f.write("\n")
        f.close()
        time.sleep(1)
