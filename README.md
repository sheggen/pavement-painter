# Raspberry Pi-controlled pavement painter

Pavement Painter is a Raspberry Pi controlled set of solenoids designed to print images to pavement using rain water. To use the Pavement Painter, you'll need to create the boards included in the Eagle files, as well as a few other controls. 

### WARNING:

Taking on this project is not for the faint at heart; there'll be lots of technical hiccups that you'll run into, and will have to solve on your own. There's hardware in addition to the software that you'll need to create, so get your soldering iron hot.  

## Requirements

- Raspberry Pi
- Python 3
- Everything included in requirements.txt and setup.sh (installable by running ```source setup.sh```)
- Physical boards (layouts included in the Pavement-painter directory)


## Installation

The code comes with a setup script. First do the apt-get installs listed at the beginning of the script. Then, running it should set up a Python Virtual Environment and pip install all the necessary components. Make sure the venv is activated before running the code, to ensure dependencies exist. To run the setup script, at the terminal enter ```source setup.sh```

## Usage

The code can most easily be ran at the terminal by running ```source run_at_boot.sh```. On the Pi, it is recommended that you do NOT run it using Thonny, as it causes a delay that will distort the print. At the terminal, we have yet to experience a delay in the printing outside of the physical limitations of the solenoids. 

## Modifying print parameters

Eventually parameters will be passed in through the above command. For now, though, I've placed all parameters at the ```__init__()``` method of the PavementPainter() class. Modify them and see what happens to your prints!

