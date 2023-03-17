from json import load
import logging
from math import isnan
from pkg_resources import Requirement, resource_filename
import sys
from time import sleep
from typing import List, Optional
from czfacsautomation.hardware import ArduinoController
from czfacsautomation.hardware import ZaberController


class HardwareController():
    """Wrapper class for the ZaberController and ArduinoController and accesses config file
    """

    def __init__(self, location: str):
        """Runs hardware setup and passes config parameters to each hardware
        
        :param location: the system location for each physical instrument
        :type location: str
        :raises FileNotFoundError: loggings critical if the hardware config file not found
        """
        
        self.filelocation = '{}{}\{}'.format('..\\config\\hardware_config\\', location, 'hardware_config.json')
        hardware_config_file = resource_filename(Requirement.parse("czfacsautomation"), self.filelocation)
        try:
            with open(hardware_config_file, 'r') as f:
                p = load(f)
            self.zaber_config = p['zaber_config']
            self.arduino_config = p['arduino_config']
            self.temp_variables = p['temperature']
            self.agitation_interval = p['agitation']['interval']
            self.next_tube_interval = p['agitation']['next_tube']
        except FileNotFoundError:
            logging.critical('Config file not found')

    def connect_hardware(self, env='prod'):
        """Connect to hardware
        
        :param env: environment as to whether in production or test mode
        :type env: str 
        """
        
        if env == 'test':
            # Change this depending on computer
            env = 'prod'
            self.next_tube_interval = 0.1
        self.zc = ZaberController(self.zaber_config, env)
        self.ac = ArduinoController(self.arduino_config, env)

    def run_complete(self):
        """Does all the connection close up after the full run is complete
        """

        logging.info("Turning off any motors that are turned on")
        self.turn_off_on_motors()
        logging.info("Homing zaber arms and closing connection")
        self.zc.home_arm(['y','z','x'])
        self.zc.disconnect()
        sol = input('Turn off solenoid valve (y/n)? ')  # get user input to turn off valve
        if sol not in ['n', 'N']:
            logging.info("Turning off solenoid valve")
            self.ac.toggle_solenoid_valve()
        self.ac.disconnect()

    def run_setup(self, tube_no: int):
        """Agitate the first tube for 30 sec then start process

        :param tube_no: The tube we are starting the process with. Goes sequentially from here
        :type tube_no: int
        """

        logging.info('Agitating the first tube for 30 sec before starting process')
        self.ac.toggle_motor(tube_no, True)
        sleep(30)
        logging.info('Done agitating first tube')


    def start_sequential_agitation(self, current_tube: int, next_tube: Optional[int]):
        """Stop agitation of current tube and agitate next tube

        :param current_tube: The tube just finished sorted
        :type current_tube: int
        :param next_tube: The motor to turn on
        :type next_tube: int or None if current_tube is the last
        """

        self.ac.toggle_motor(current_tube, False)
        if next_tube is not None:
            logging.info("Turning on tube {}".format(next_tube))
            self.ac.toggle_motor(next_tube, True)
        else:
            logging.info("No next tube to turn on")


    def start_sort(self, tube_no: int):
        """Complete all the steps to setup the sort

        :param tube_no: The tube containing the sample to sort
        :type tube_no: int
        :raises: Any Zaber exception requires restart and reinitialization of Zaber connection
        """
        
        try:
            self.zc.prep_tube_housing_pickup(tube_no)
            self.zc.pick_tube_y(tube_no)
            self.zc.go_to_facs(True)
            self.zc.pick_or_drop_tube(False)
        except:
            raise

    def finish_sort(self, tube_no: int):
        """Return the tube to the tube holder when sorting is finished

        :param tube_no: The tube containing the sample finishes sorting
        :type tube_no: int
        :raises: Any Zaber exception requires restart and reinitialization of Zaber connection
        """
        
        try:
            self.zc.go_to_facs(False)
            self.zc.pick_or_drop_tube(True)
            self.zc.prep_tube_housing_dropoff(tube_no)
            self.zc.pick_or_drop_tube(False, tube_no)
        except:
            raise
            
    def temperature_data(self) -> str:
        """Compare the data to the threshold and see if it is out of range

        :return: Any error message due to out of range data or lost connection
        :type: str
        """

        msg = ''
        temp = self.ac.read_temp()  # get the list from here
        if temp is None:
            msg = "Did not receive temperature data from Arduino"
            logging.warning(msg)
            return msg
        else:
            i = 0
            for t in temp:
                if t > self.temp_variables['upper_threshold'] or t < self.temp_variables['lower_threshold']:
                        msg = '{} Sensor: {}, Outside Range: {}\n'.format(msg, i, t)
                elif isnan(t):
                    msg = '{} Sensor: {} Disconnected: {}\n'.format(msg, i, t)
                i += 1
        if msg == '':
            logging.info('All temperature readings are as expected')
        else:
            head = 'The following errors are detected in the temperature reading: \n'
            threshold_desc = 'Upper Threshold = {}'.format(self.temp_variables['upper_threshold'])
            threshold_desc = '{}, Lower Threshold = {}'.format(threshold_desc,
                                                            self.temp_variables['lower_threshold'])
            msg = '{}{}{}'.format(head, msg, threshold_desc)
            logging.warning(msg)
        return msg

    def agitate_multiple_motors(self, motors, turn_on: bool= True):
        """Send cmd to agitate multiple motors based on motor list

        Checks the status of the list of motors, and toggles the ones
        that do not match the desired state.

        :param motors: List of motors
        :type motors: List[int]
        :param turn_on: The desired state for each motor, defaults to True
                        True = on
        :type turn_on: bool
        """
        
        self.ac.toggle_multiple_motors(motors, turn_on)

    def turn_off_on_motors(self):
        """Switch off all the motors that are on
        """

        logging.info('Switching off all on motors')
        motor_state = self.ac.read_motor_status()
        on_motors = []
        if motor_state is not None:
            for i in range(len(motor_state)):
                if motor_state[i] == 1:
                    on_motors.append(i)
            self.ac.toggle_multiple_motors(on_motors, False)
            logging.info("Turning off motors {}".format(on_motors))