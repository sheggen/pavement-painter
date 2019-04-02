import obd

# connection = obd.OBD() # auto-connects to USB or RF port
obd.logger.setLevel(obd.logging.DEBUG)

ports = obd.scan_serial()      # return list of valid USB or RF ports
print (ports)                    # ['/dev/ttyUSB0', '/dev/ttyUSB1']
connection = obd.Async(ports[0]) # connect to the first port in the list

connection.watch(obd.commands.SPEED) # keep track of the RPM

connection.start() # start the async update loop

print (connection.query(obd.commands.SPEED)) # non-blocking, returns immediately
