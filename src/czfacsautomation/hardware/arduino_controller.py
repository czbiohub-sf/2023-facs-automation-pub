import logging
import serial
from time import sleep
from typing import Dict, List, Optional, Union
from czfacsautomation.hardware.simulators.arduino_sim import Arduino


class ArduinoController():
    """Communicate with Arduino over serial to toggle motors and read temperature
    """

    def __init__(self, config: Dict[str, Union[int, str]], env='prod'):
        """Starts the serial connection

        :param config: The arduino specific parameters defined in
            the hardware_config.json file
        :type config: dict {'port': <name of the serial port>,
            'baudrate': <the int baudrate>} 
        :param env: The environment to run the Arduino Controller.
        :type env: string, either 'prod' or 'dev'
        """

        self.arduino = None
        self.retry_temp = True
        self.retry_cmd = True
        self.env = env
        self._connect(config['port'], config['baudrate'])

    def _connect(self, serial_port: str, baudrate: int):
        """Start the serial communication with the arduino

        :param serial_port: Name of the serial port
        :type serial_port: str
        :param baudrate: Connection baudrate
        :type baudrate: int
        :raises SerialException: Logs critical if the serial port is unavailable
        """

        try:
            if self.env == 'prod':
                logging.info('Connecting to Arduino')
                try:
                    self.arduino = serial.Serial(serial_port, baudrate, timeout=3)
                except Exception as e:
                    logging.critical('Exception with connection to Arduino: {}'.format(e))
                self._okay_resp_checker('Ready')
            elif self.env == 'dev':
                logging.info('Connecting to mock Arduino')
                self.arduino = Arduino(serial_port, baudrate, timeout=3)
                self.arduino.ready()
                self._okay_resp_checker('Ready')
        except serial.SerialException:
            logging.critical('Could not connect to arduino')
    
    def disconnect(self):
        """Close the serial connection
        """

        self.arduino.close()
        logging.info('Closed Arduino Connection')

    def _send_cmd(self, cmd: str):
        """Send serial cmd to the arduino

        :param cmd: The command to send, without newline delimiter added
        :type cmd: str
        :raises SerialException: Logs error if the serial connection 
                                 is lost while sending cmd
        """

        cmd_b = '{}\n'.format(cmd).encode()
        try:
            self.arduino.write(cmd_b)
            self.arduino.flush()
        except serial.serialutil.SerialException:
            logging.critical('Connection Lost. Device not configured')
            self.arduino.close()

    def _get_response(self) -> str:
        """Get response from arduino. Response should be one line
        
        :raises SerialException: Logs critical if the serial connection is lost 
                                 while requesting response
        :return: The serial communication from the arduino.
        :rtype: str
        """

        try:
            return self.arduino.readline().decode()
        except serial.serialutil.SerialException:
            logging.critical('Connection Lost. Device not configured')
            self.arduino.close()

    def _okay_resp_checker(self, expected: str) -> bool:
        """Compares expected response with actual response

        Logs if the response is empty or not expected. This method is called
        if the response is not cruicial and the response is simply logged. 

        :param expected: The expected response without newline delimiter
        :type expected: str
        :return: A bool as to whether a response was received.
        :rtype: bool
        """

        resp = self._get_response()
        expected = '{}\r\n'.format(expected)
        if resp == '':
            logging.warning('Timed out, did not get a response')
            return(False)
        if resp != expected:
            logging.warning('Unexpected response: {}, Expected: {}'.format(resp, expected))
            return(True)
        else:
            logging.info('Response is okay: {}, Expected: {}'.format(resp, expected))
            return(True)

    def _parse_response(self, data_msg: str, data_type, caller_method, caller_args = None
                        ) -> Optional[List[Union[int, float]]]:
        """Parse the response into a list and resend command if response is invalid

        The expected response is a string of data separated by comma.
        Retries once if the response does not match expected, this is to
        counter data loss due to pausing the software. This method is called 
        when the response is used to determine next steps.

        :param data_msg: The description of the data to receive
        :type data_msg: str
        :param data_type: What to convert the data to i.e. float or int
        :type data_type: str to num converter method
        :param caller_method: The method to call to try again
        :type caller_method: Method of ArduinoController class
        :param caller_args: List of arguments needed for the caller method, defaults to None
        :type caller_args: argument list, optional
        :raises ValueError: If the str can't be converted to float, meaning 
                            the response is unexpected
        :raises AttributeError: Logs critical if the serial connection is lost 
        :return: A list of the response either as int or float, None if invalid
        :rtype: Optional[List[Union[int, float]]
        """

        resp = self._get_response()
        try:
            data = [data_type(t) for t in resp.split(',')]  # NaN is accepted as float
            self.retry_cmd = True
            return data
        except ValueError:
            logging.critical('Invalid {} data: \'{}\''.format(data_msg, resp))
            if self.retry_cmd:
                self.retry_cmd = False
                logging.info('Retrying to get {} data'.format(data_msg))
                if caller_args is None:
                    caller_method()
                else:
                    if len(caller_args) == 1:
                        caller_method(caller_args[0])
                    elif len(caller_args) == 2:
                        caller_method(caller_args[0], caller_args[1])          
            else:
                logging.critical('Invalid response in 2nd try aswell')
        except AttributeError:
            logging.critical('Lost connection!')

    def toggle_motor(self, motor_no: int, turn_on: bool=True):
        """Send command to toggle the motor on/off

        The expected response is a int list [<motor_num>, <old_state>, <new_state>]

        :param motor_no: The motor to toggle, the number is based on the position.
                         A number between 0-17
        :type motor_no: int
        :param turn_on: True: turn on motor, False: turn off motor, defaults to True
        :type turn_on: bool, optional
        """

        msg = 'on' if turn_on else 'off'
        motor_state = self.read_motor_status(motor_no)
        if motor_state is not None:
            if motor_state[0] != turn_on:
                if turn_on:
                    cmd = 'S,[{}]'.format(motor_no)
                else:
                    cmd = 'E,{}'.format(motor_no)
                self._send_cmd(cmd)
                self._motor_expected_resp(motor_no, turn_on)
                logging.info('Turning motor {} {}'.format(motor_no, msg))
            else:
                logging.info('Motor {} is already {}'.format(motor_no, msg))
    
    def toggle_multiple_motors(self, motors: List[int], turn_on: bool=True):
        """Toggle multiple motors, assuming the status is already checked

        :param motors: The list of the motor numbers to toggle
        :type motors: List[int]
        :param turn_on: True = Turn all on, defaults to True
        :type turn_on: bool, optional
        """
        
        motors_to_toggle = []

        # Sort out the ones that are not already in the turn_on state
        for m in motors:
            motor_state = self.read_motor_status(m)
            if motor_state is not None:
                if motor_state[0] != turn_on:
                    motors_to_toggle.append(m)
        if turn_on:
            self._send_cmd('S,{}'.format(motors_to_toggle))
        for m in motors_to_toggle:
            if not turn_on:
                self._send_cmd('E,{}'.format(m))
            self._motor_expected_resp(m, turn_on)

    def _motor_expected_resp(self, motor_no: int, turn_on: bool):
        """The expected response when toggling a motor

        :param motor_no: The motor toggled
        :type motor_no: int
        :param turn_on: True: turned on, False: turned off
        :type turn_on: bool
        """
        
        if not turn_on:
            expected_encoder_resp  = 'Detected'
            while (True):
                encoder = self._okay_resp_checker(expected_encoder_resp)
                if encoder:
                    break
        toggle_state = '{},{}'.format(0,1) if turn_on else '{},{}'.format(1,0)
        expected_rep = '[{},{}]'.format(motor_no, toggle_state)
        self._okay_resp_checker(expected_rep)


    def change_speed(self, pwm: int):
        """Send command to update speed of all the motors

        The method is currently not used in the sorting automation sequence.
        The current expected response is 'ok'

        :param pwm: The new PWM value to set for all the motors
        :type pwm: int
        """

        self._send_cmd('P,{}'.format(pwm))
        self._okay_resp_checker('ok')

    def read_temp(self) -> Optional[List[float]]:
        """Requests and reads the temperature data

        :return: list of the temperature readings from each sensor
        :rtype: list of float values, None if unexpected response after 2 tries
        """

        self._send_cmd('READ_TEMP')
        return self._parse_response('temperature', float, self.read_temp)

    def read_motor_status(self, motor_num: int=-1) -> Optional[List[int]]:
        """Requests and returns the status of the motor

        :param motor_num: The motor to read, -1 for all, defaults to -1
        :type motor_num: int, optional
        :return: The motor status as a list
        :rtype: Optional[List[int]]
        """
        
        cmd = 'M,{}'.format(motor_num)
        self._send_cmd(cmd)
        return self._parse_response('motor status', int, self.read_motor_status, [motor_num])

    def toggle_solenoid_valve(self):
        """Toggle the solenoid valve when the run is complete
        """

        self._send_cmd('VALVE')