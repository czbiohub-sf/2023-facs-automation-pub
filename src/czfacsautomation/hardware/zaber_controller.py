import logging
from time import sleep
from typing import Optional, Tuple
from zaber_motion import Library, Units
from zaber_motion.ascii import Connection, Axis
from zaber_motion.exceptions.connection_failed_exception import ConnectionFailedException
from zaber_motion.exceptions.movement_failed_exception import MovementFailedException


class ZaberController():
    """Communicate with Zaber devices over serial to move the stage or the gripper
    """

    def __init__(self, config: dict, env='prod'):
        """Setup the serial connection between with the zaber device

        :param config: The zaber specific parameters defined in the 
                    hardware_config.json file
        :type config: dict {'port': <name of the serial port>,
                    'tube0': <x,y,z>, ...} 
        :param env: The environment to run the Zaber Controller.
        :type env: string, either 'prod' or 'dev'
        """

        #TODO add the retry to grab
        self.zaber = None
        self.stage_axes = {}
        self.gripper = None
        self.config = config
        self.env = env
        self._connect()

    def _connect(self):
        """Create a serial communication with the zaber devices

        :raises ConnectionFailedException: Logs critical if the connection fails
        """

        try:
            if self.env == 'prod':
                logging.info('Establishing connection with Zaber devices')
                self.zaber = Connection.open_serial_port(self.config['port'])
                logging.info('Zaber devices successfully connected')
                # Set the names and velocities for each axis
                self._set_axis(self.zaber.detect_devices()[0])
                self.gripper = self.zaber.detect_devices()[1].get_axis(1)
                self.gripper.settings.set("maxspeed", self.config['max_speed']['gripper'], Units.VELOCITY_MILLIMETRES_PER_SECOND)
                logging.info('Homing all')
                self.home_arm()
                self._move_z_tube_housing(0, True)
            elif self.env == 'dev':
                logging.info('Establishing connection with mock Zaber devices')
                self.zaber = Zaber(self.config['port'])
                logging.info('Zaber devices successfully connected')
                # Set the names for each axis
                self._set_axis(self.zaber.detect_devices()[0])
                self.gripper = self.zaber.detect_devices()[1].get_axis(1)
                logging.info('Homing all')
                self.home_arm()                
        except ConnectionFailedException:
            logging.critical("Could not make connection to zaber stage")
            raise

    def disconnect(self):
        """Closes the serial Connection
        """

        self.zaber.close()
        logging.info('Closed Zaber device connection')

    def _set_axis(self, stage):
        """Set the x y z stage dictionary variables based off the peripheral name

        :param stage: zaber x,y,z stage
        :type stage: tuple of zaber device objects
        """

        for i in range(3):
            name = stage.get_axis(i+1).peripheral_name
            if name == 'LSQ450D-E01T3A':
                self.stage_axes.update({'x': stage.get_axis(i+1)})
                self.stage_axes['x'].settings.set("maxspeed", self.config['max_speed']['x'], Units.VELOCITY_MILLIMETRES_PER_SECOND)
            elif name == 'LSQ075B-T4A-ENG2690':
                self.stage_axes.update({'y': stage.get_axis(i+1)})
                self.stage_axes['y'].settings.set("maxspeed", self.config['max_speed']['y'], Units.VELOCITY_MILLIMETRES_PER_SECOND)
            elif name == 'LSQ150B-T3A':
                self.stage_axes.update({'z': stage.get_axis(i+1)})
                self.stage_axes['z'].settings.set("maxspeed", self.config['max_speed']['z'], Units.VELOCITY_MILLIMETRES_PER_SECOND)

    def home_arm(self, arm: Optional[list]=None):
        """Home either all or a subset of the devices

        The devices include the xyz stage and the grippers. The order in which
        it homes is dependent on the list passed. The order is important 
        to ensure the device does not crash while homing.

        :param arm: list of the devices to home in the desired sequence,
                    ['x','y','z','g']
                    defaults to None, if None homes everything
        :type arm: list of str, optional
        :raises: Any Zaber exception requires restart and reinitialization of Zaber connection
        """
        
        home = ['g','y','z','x'] if arm == None else arm
        for h in home:
            try:
                self._move_arm(h)
            except:
                raise

    def _move_x_tube_housing(self, tube_no: int):
        """Move to the x position for the tube in the tube housing

        :param tube_no: The tube no for the x position
        :type tube_no: int
        :raises: Any Zaber exception requires restart and reinitialization of Zaber connection
        """

        if tube_no < 9:  # lower rail
            dist = self.config['tube0']['x'] - tube_no*self.config['inner_spacing']['spacing']
        else:  # upper rail
            dist = self.config['tube9']['x'] - (tube_no - 9)*self.config['inner_spacing']['spacing']
        try:
            self._move_arm('x', dist)
        except:
            raise
            
    def _move_y_tube_housing(self, tube_no: int, is_ypickup: bool=False):
        """Move to the y position for the tube in the tube housing

        :param tube_no: The tube no for the x position
        :type tube_no: int
        :param is_ypickup: True: go to the out position for y 
                        to prepare for pickup, defaults to False
        :type is_ypickup: bool, optional
        :raises: Any Zaber exception requires restart and reinitialization of Zaber connection
        """

        pos = 'out' if is_ypickup else 'in'
        rail = 'upper_rail' if tube_no >= 9 else 'lower_rail'
        try:
            self._move_arm('y', self.config[rail]['y'][pos])
        except:
            raise

    def _move_z_tube_housing(self, tube_no: int, is_ypickup: bool=False):
        """Move to the z position for the tube in the tube housing

        :param tube_no: The tube no for the x position
        :type tube_no: int
        :param is_ypickup: True: go to the low position for z, 
                        to prepare for pickup by y, defaults to False
        :type is_ypickup: bool, optional
        :raises: Any Zaber exception requires restart and reinitialization of Zaber connection
        """

        pos = 'low' if is_ypickup else 'high'
        rail = 'upper_rail' if tube_no >= 9 else 'lower_rail'
        try:
            self._move_arm('z', self.config[rail]['z'][pos])
        except:
            raise

    def _move_arm(self, arm: str, dist: Optional[float]=None, is_relative: bool=False):
        """Move any arm 'x','y','z','g' by a fixed amount

        :param arm: The arm to move x' or 'y' or 'z' or 'g' ('g' for gripper)
        :type arm: str
        :param dist: The distance to move in mm, if None: home arm, defaults to None
        :type dist: float, optional
        :param is_relative: True: move a relative distance, False: move an absolute distance,
                    defaults to False
        :type is_relative: bool, optional
        :raises MovementFailedException: Logs if the desired position is not reached
        :raises ConnectionFailedException: Logs if the zaber connection fails
        """

        a = 'gripper' if arm == 'g' else arm
        device_arm = self.gripper if arm == 'g' else self.stage_axes[arm]
        try:
            if dist is None:
                device_arm.home()
            elif is_relative:
                device_arm.move_relative(dist, Units.LENGTH_MILLIMETRES)
                #curpos = self.gripper.get_position(unit=Units.LENGTH_MILLIMETRES)
                #print(curpos)
            else:
                device_arm.move_absolute(dist, Units.LENGTH_MILLIMETRES)
                #curpos = self.gripper.get_position(unit=Units.LENGTH_MILLIMETRES)
                #print(curpos)
        except MovementFailedException:
            curpos = device_arm.get_position(unit=Units.LENGTH_MILLIMETRES)
            logging.critical('Failed to move {} arm'.format(a))
            logging.critical('Stuck At: {}, Desired Pos: {}'.format(curpos, dist))
            raise
        except ConnectionFailedException:
            logging.critical('Zaber Connection Failed')

    def _grab_tube(self):
        """Closes the gripper arm to grab the tube

        :raises MovementFailedException: Expected exception, as the gripper should
                    fail to reach max position. The difference determines if grabbed
        :raises ConnectionFailedException: Logs if the zaber connection fails
        """

        try:
            #curpos = self.gripper.get_position(unit=Units.LENGTH_MILLIMETRES)
            #print(curpos)
            self.gripper.move_max()
            #curpos = self.gripper.get_position(unit=Units.LENGTH_MILLIMETRES)
            #print(curpos)
        except MovementFailedException:
            curpos = self.gripper.get_position(unit=Units.LENGTH_MILLIMETRES)
            print(curpos)
            if curpos - self.config['claw']['max_position'] < self.config['claw']['feedback']:
                logging.critical('Tube was not grabbed! Retrying')
                logging.critical('Gripper Current Position: {}'.format(curpos))
                #print(curpos)
                #self._retry_grab_tube()
                #raise
            else:
                logging.critical('Tube grabbed successfully')
                logging.critical('Gripper Current Position: {}'.format(curpos))
                #print(curpos)
        except ConnectionFailedException:
            logging.critical('Zaber Connection Failed')

    def _retry_grab_tube(self):
        """Retry grabbing the tube before reporting error
        """

        print('RETRY GRABBING TUBE FUNCTION CALLED')

    def _move_slow(self, axis: str, dist: float):
        """Move the axis at a slower speed till the distance is reached

        :param axis: 'x'/'y'/'z'
        :type axis: str
        :param dist: The absolute distance to move in mm
        :type dist: float
        """
        
        curpos = self.stage_axes[axis].get_position(unit=Units.LENGTH_MILLIMETRES)
        rel_dist = dist - curpos
        velocity = 5
        self.stage_axes[axis].move_velocity(velocity, unit=Units.VELOCITY_MILLIMETRES_PER_SECOND)
        sleep(rel_dist/velocity)
        self.stage_axes[axis].stop()

    def prep_tube_housing_pickup(self, tube_no: int):
        """Prepares for tube pick up by going to the position at tube housing

        The sequence of the arm movement is important to avoid crashing and 
        to accommodate picking up by moving into y.

        :param tube_no: The tube to pick up
        :type tube_no: int
        :raises: Any Zaber exception requires restart and reinitialization of Zaber connection
        """
        
        try:
            self._move_x_tube_housing(tube_no)
            self._move_arm('g', self.config['claw']['tube_clearance'])
            self._move_z_tube_housing(tube_no, True)
            logging.info('Ready to pick up tube at location: {}'.format(tube_no))
        except:
            raise

    def prep_tube_housing_dropoff(self, tube_no: int):
        """Prepares to drop off the tube by going to the position at tube housing

        :param tube_no: The tube to drop off
        :type tube_no: int
        :raises: Any Zaber exception requires restart and reinitialization of Zaber connection
        """
        
        try:
            self._move_x_tube_housing(tube_no)
            self._move_z_tube_housing(tube_no)
            self._move_y_tube_housing(tube_no)
            logging.info('Ready to drop off tube at location: {}'.format(tube_no))
        except:
            raise

    def go_to_facs(self, is_dropoff: bool):
        """Go to FACS location for tube pick up or drop off

        At the FACS location both pick and drop preparation are the same as the tube
        is picked up/dropped off by moving along z. The tube will not be on an off axis,
        and does not need alignment before pick up.

        :param is_dropoff: True: the movement is to grab tube, False: release tube
        :type is_dropoff: bool
        :raises: Any Zaber exception requires restart and reinitialization of Zaber connection
        """
        
        try:
            self._move_arm('x', self.config['facs_location']['x'])
            if is_dropoff:
                self._move_arm('z', self.config['facs_location']['z']['high'])
            self._move_arm('y', self.config['facs_location']['y'])
            logging.info('At the FACS location')
        except:
            raise

    def pick_tube_y(self, tube_no: int):
        """Pick up tube by moving forward in y to grab it.

        First move in y then grab the tube, then home z to raise the tube,
        finally home y to retrieve the tube.

        :param tube_no: The tube to grab
        :type tube_no: int
        :raises: Any Zaber exception requires restart and reinitialization of Zaber connection
        """
        
        try:
            rail = 'upper_rail' if tube_no >= 9 else 'lower_rail'
            self._move_arm('y', self.config[rail]['y']['in'])
            self._grab_tube()
            self._move_arm('z', self.config[rail]['z']['high'])
            self._move_arm('y', self.config['Sony_clearance'])
            logging.info('Picked up tube from the tube housing')
        except:
            raise

    def pick_or_drop_tube(self, is_pickup: bool, tube_no: Optional[int]=None):
        """Pick up or drop tube by moving down on z

        First move the arm down in z, then either grab or release tube, then raise
        gripper, and move back in y.

        :param is_pickup: True: the movement is to grab tube, False: release tube
        :type is_pickup: bool
        :param tube_no: The tube_no at the tube housing, None: at the FACS, defaults to None
        :type tube_no: int, optional
        :raises: Any Zaber exception requires restart and reinitialization of Zaber connection
        """
        
        try:
            if tube_no is None:
                self._move_arm('z', self.config['facs_location']['z']['low'])
            else:
                rail = 'upper_rail' if tube_no >= 9 else 'lower_rail'
                self._move_arm('z', self.config[rail]['z']['return'])
            if is_pickup:
                self._grab_tube()
                self._move_arm('z', self.config['facs_location']['z']['high'])
                logging.info('Picked up tube from the FACS')  # z pick up only used for FACS 
            else:
                self._move_arm('g', self.config['claw']['tube_clearance'])
                loc = 'FACS' if tube_no is None else 'tube housing location {}'.format(tube_no)
                logging.info('Dropped off tube at {}'.format(loc))
            self._move_arm('y', self.config['Sony_clearance'])
        except:
            raise