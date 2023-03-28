from json import load
import logging
import sys
from pkg_resources import Requirement, resource_filename
from czfacsautomation.hardware import ArduinoController

def main(location = sys.argv[1]):
    """Connect to the Arduino Controller and actuate the solenoid valve to
       begin cooling the tube housing.
       
    :param location: the system location for each physical instrument
    :type location: str
    :raises FileNotFoundError: If json hardware config file is not found in the location the program quits
    """
        
    filelocation = '{}{}\{}'.format('config\\hardware_config\\', location, 'hardware_config.json')
    hardware_config_file = resource_filename(Requirement.parse("czfacsautomation"), filelocation)
    
    try:
        with open(hardware_config_file, 'r') as f:
            p = load(f)
        arduino_config = p['arduino_config']
    except FileNotFoundError:
        logging.critical('Config file not found')    
        
    ac = ArduinoController(arduino_config, 'prod')
    
    ac.toggle_solenoid_valve()
    logging.info("Actuated Solenoid")
    
    ac.disconnect()
    logging.info("Disconnected from Arduino")
           
if __name__ == "__main__":
    ChillHouse = main(sys.argv[1])