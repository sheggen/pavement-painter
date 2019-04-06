import obd


class OBD2:
    def __init__(self):
        # obd.logger.setLevel(obd.logging.DEBUG)
        try:
            self.connection = obd.Async() # auto-connects to USB or RF port
        except:
            try:
                self.ports = obd.scan_serial()      # return list of valid USB or RF ports
                print (self.ports)                    # ['/dev/ttyUSB0', '/dev/ttyUSB1']
                self.connection = obd.Async(self.ports[0]) # connect to the first port in the list
            except:
                pass
        self.connection.watch(obd.commands.SPEED)
        self.connection.start()

    def get_speed(self):
        return self.connection.query(obd.commands.SPEED) # non-blocking, returns immediately

if __name__ == "__main__":
    o = OBD2()
    while True:
        print("Speed: ", o.get_speed())
