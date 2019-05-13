from LiveCamera import *
from PavementPainter import *


# Create a camera object
lc = LiveCamera(2)

# Create a PavementPainter object
pp = PavementPainter(1, lc)

# Run them both on their own threads
pp.start()
lc.start()

