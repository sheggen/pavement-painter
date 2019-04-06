import obd
import datetime, time

class OBD2:
    """
    Handles connection to the OBD2 sensor and returns data

    """
    def __init__(self):
        # obd.logger.setLevel(obd.logging.DEBUG)
        try:
            self.connection = obd.Async()               # auto-connects to USB or RF port
        except:
            try:
                # Try connecting a slightly less automatic way
                self.ports = obd.scan_serial()          # return list of valid USB or RF ports
                print (self.ports)                      # ['/dev/ttyUSB0', '/dev/ttyUSB1']
                self.connection = obd.Async(self.ports[0])  # connect to the first port in the list
            except:
                pass
        self.connection.watch(obd.commands.SPEED)       # Watch the speed value from OBD2
        self.connection.start()

    def get_speed(self):
        """
        Returns the speed from the OBD2

        :return: speed of the vehicle in kmph
        """
        return self.connection.query(obd.commands.SPEED)  # non-blocking, returns immediately

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
            f.write(str(9.525/(int(s.split(" ")[0])*1000000/3600)))
        except:
            pass
        f.write("\n")
        f.close()
        time.sleep(1)
