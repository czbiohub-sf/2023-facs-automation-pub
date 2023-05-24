import datetime
import logging
from multiprocessing import Process as mProcess
from multiprocessing import Event
import os
from pandas import read_csv
from psutil import Process as pProcess
from pynput import keyboard
import sys
from time import sleep, time
from threading import Timer, Lock
from typing import Tuple, List, Dict, Optional
from czfacsautomation.hardware.arduino_controller import ArduinoController
from czfacsautomation.hardware.hardware_controller import HardwareController
from czfacsautomation.slack.slack_facs import SlackFacs
from czfacsautomation.sorting.controller import Controller
from czfacsautomation.sorting.sorting_automation import Sort, MockSort


timestamp = datetime.datetime.now()
tme = timestamp.strftime("%Y-%m-%d")
log_filepath = f"../../logs"
log_filename = f"{log_filepath}/{tme}_log"
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())
logging.basicConfig(filename=log_filename, filemode='a', 
                   format='%(asctime)s - %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
log.setLevel(logging.INFO)

# Set log to terminal
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s',"%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
log.addHandler(handler)

def single_sort(is_first: bool, controller, exp_name: str, sample: str, well: str, e, env='prod'):
    """Run a single sort from the sorting automation class
    
    :param is_first: If it is the first sample
    :type is_first: bool
    :param controller: instance of the controller class used in manipulating the Sony GUI
    :type controller: type
    :param exp_name: Name of the experiment received from the user input
    :type exp_name: str
    :param sample: Name of the sample being sorted
    :type sample: str
    :param well: Location within the 96 well plate for the sample
    :type well: str
    :param e: instance of multiprocessing event class for whether to agitate the sample tube
    :type e: type
    :param env: state of the software for production or development testing
    :type env: str
    """
    
    if env == 'prod':
        sorter = Sort(is_first, controller)
        sorter._prep()
        sorter._profiling(sample)
        sorter._gating(exp_name, sample)
        sorter._sorting(sample, well, e)
        log.info("Finishing up sort")
        
    elif env == 'dev':
        sorter = MockSort()
        sorter._prep()
        sorter._profiling(sample)
        sorter._gating(exp_name, sample)
        sorter._sorting(sample, well, e)

    elif env == 'test':
        sleep(2)
        print("Finishing 'Gate'")
        e.set()
        print(f"Event should be set: {e.is_set()}")
        sleep(15)
        print("Finishing up sort")

class FACSAutomation():
    """Run the full FACS Automation Process
    """

    def __init__(self, location, env='prod'):
        """Initializes instance attributes for threads, locks, classes, flags,
        and misc. instance attribues
        
        :param location: the system location for each physical instrument
        :type location: str
        :param env: environment as to whether in production or test mode
        :type env: str
        """
    
        log.info("Starting FACS Automation Software")
        
        self.facs = None
        self.temp_thread = None
        self.agitation_thread = None
        self.error_check = None
        
        self.pause_lock = Lock()
        self.arduino_call_lock = Lock()
        
        self.env = env
        self.location = location
        self.user = None
        self.slk_timestamp = None
        self.data_dict = None
        self.remaining_tubes = None
        self.agitation_event = None
        self.first_agitation_call = True
        self.stop = False
        self.interrupt = False
        self.error_flag = False
        self.no_slack = None
        
        self.hc = None
        self.c = None
        self.slk = None
        
    def _connect_hardware(self):
        """Initializes the Hardware Controller class and makes connections

        :raises: Any exception that doesn't instantiate the class and requires restart
        """
        try:
            self.hc = HardwareController(self.location)
            self.hc.connect_hardware(self.env)
        except:
            raise Exception
    
    def _initialize_classes(self):
        """Initialize the required classes (GUI Controller, Slackbot)
        
        :raises: Any exception that doesn't instantiates the classes requires restart
        """
        
        try:
            self.slk = SlackFacs(self.location)
        except:
            log.info("Slack cannot connect.") 
            self.no_slack = input("Do you want to proceed without Slack messaging (y/n)?")
            if self.no_slack in ['n','N']:
                raise Exception
            
        try:
            self.c = Controller()
        except:
            raise Exception
        
    def _start_threads(self):
        """Starts all monitoring threads and the keyboard interrupt listener
        """
        
        log.info("Start sequence to read key strokes for interrupts")
        log.info("F5 - pause, F6 - resume, F7 - stop")
        self.start_keyboard_listener()
        log.info("Start thread to read temperature data")
        self.run_temperature_thread()
        log.info("Start thread for interval agitation")
        self.run_agitation_thread() 
        log.info("starting thread for monitoring Sony errors")
        self.error_check_thread()
        
    def _user_setup(self) -> Tuple[str]:
        """Gets various information from the user regarding the experiment and
        starts agitation of the first tube
        
        :raises: Any exception that fails to setup the Sony instrument and software
        :return: name of the experiment
        :rtype: Tuple[str]
        """
        
        while True:
            user = input('Enter User Name: ')
            valid_user = self.slk.userCheck(user)
            if valid_user:
                self.user = user
                break
            else:
                log.info(f"{user} is not a valid user. Please enter a valid user.")
        self.user = (self.user).upper()
        log.info("Entered User Name is {}".format(self.user))
        
        try:
            log.info("Getting the name of the experiment")
            exp_name = self.get_experiment_name()
            log.info("Starting experiment \'{}\'".format(exp_name))
            file_name = "sort_samples.csv"
            log.info("Reading \'{}\' to obtain the sample metadata".format(file_name))
            self.data_dict = self.get_sample_metadata(file_name)
            self.slk_timestamp = self.slk.sendMessage('FACS_startup', self.user, self.no_slack)
            self.remaining_tubes = self.data_dict['Tube']
            log.info("Remaining Tubes {}".format(self.remaining_tubes))    
        except:
            log.info('Exiting automation program during setup.')
            raise Exception
            
        return exp_name 
    
    def cleanup(self):    
        """Closes up any of the threads and the hardware connection 
        """
        
        self.stop = True # Finishes any agitation thread if the sort finishes
        log.info('About to enter done protocol function.')
        self.done_protocol()  # called if stopped or when method finishes

    ##########################
    # Initialization Methods #
    ##########################

    def start_solenoid(self):
        """Actuate the solenoid valve to start cooling the tube housing.
        """

        self.hc.ac.toggle_solenoid_valve()
        log.info('Solenoid valve actuated to cool housing, a minimum of 10 min is needed to reach equilibrium temperature.')
        
    def get_experiment_name(self) -> Tuple[str]:
        """Ask user for experiment name and return
        
        :raises: When the experiment name is incorrect and will crash the program if continued. The software must be restarted.
        :return: name of the experiment
        :rtype: Tuple[str]
        """
        
        log.info("Automatically searching for experiment name...")
        sleep(2)
        found_expt_name = self.c.scroll_experiment_bar("EXPERIMENT_ICON",step=10)
        if found_expt_name:
            exp_name = self.c.read_experiment_name()
            self.c.return_to_git()
            correct_name = input(f"Please confirm if correct experiment name (MUST BE EXACT): \'{exp_name}\'? (y/n):")
        else:
            correct_name = 'n'
        if correct_name in ['n','N']:
            while(True):
                exp_name = input('Please type in the name of the experiment (case sensitive) and hit Enter: ')
                if input('Is the experiment name \'{}\' (y/n)? '.format(exp_name)) in ['y','Y']:
                    break

        if exp_name.find("_") != -1:
            log.critical("Invalid experiment name.")
            log.info("Experiment names cannot contain underscores. Please rename the experiment name you have in the Cell Sorter Software if it contains underscores, and restart the automation program.")
            raise Exception
            
        self.c.find_bottom_experiment_bar()
        return exp_name

    def get_sample_metadata(self, file_name: str) -> Dict[str, List[str]]:
        """Read the csv file and retrieve the sample name list and well list to sort into
        Requests the starting tube number so that it is possible to restart an experiment in the
        middle of a sorting group.

        :param file_name: the name of the csv file to read from
        :type file_name: str
        :raises FileNotFoundError: If csv file is not found in the location the program quits
        :raises ValueError: If the starting tube number is not found in csv file
        :raises KeyError: If 'Tube' or 'Name' or 'Well' column headers are not found in csv file
        :return: The metadata in a dictionary after passing the try blocks
        :rtype: Dict[str, List[str]]
        """
        
        try:
            samples = read_csv(f"czfacsautomation/integration/{file_name}")
        except FileNotFoundError:
            log.critical('Sorting File Not Found!')
            log.info('Restart process after ensuring {} exists in current directory'.format(file_name))
            raise
            
        while(True):
            log.info('Please type in the tube to start the sorting from and hit Enter')
            start_indx = int(input("The first tube #: "))
            try:
                start_tube_index = samples.index[samples['Tube'] == start_indx].tolist()
                
                if not start_tube_index:
                    raise ValueError
                if len(start_tube_index) > 1:
                    log.info('There are multiple rows with that tube number. Which row do you want to start?')
                    print(samples['Name'][start_tube_index])
                    start_index = int(input("Type the row to start and hit Enter: "))
                else:
                    start_index = start_tube_index[0]
                if samples['Tube'][start_index] != start_indx:
                    raise ValueError
                break
            except ValueError:
                print('Invalid entry. Starting tube not found in list.')
                raise
        
        try:
            has_changed = False
            sample_list_len = len(samples['Tube'])
            tube = [samples['Tube'][t] - 1 for t in range(start_index, sample_list_len)] 
            name = [samples['Name'][t] for t in range(start_index, sample_list_len)]
            well = [samples['Well'][t] for t in range(start_index, sample_list_len)]
            for i in range(len(name)):
                s = str(name[i])
                idx = s.find("_")
                if idx != -1:
                    # Rename underscores to dashes
                    log.info(f"Sample name '{s}' is invalid. Underscores will be replaced with dashes.")
                    name[i] = f"{name[i][:idx]}-{name[i][idx+1:]}"
                    log.info(f"Changing to {name[i]}")
                    samples.loc[i, 'Name'] = name[i]
                    has_changed = True
                    
            if has_changed:
                log.info(f"CSV file {file_name} was overwritten with valid sample names.")
                samples.to_csv(file_name, index=False)

            data_dict = {'Tube': tube, 
                        'Name': name, 
                        'Well': well}
        except KeyError as e:
            log.critical('Could not find column with name: {}'.format(e))
            raise
        return data_dict

    def experiment_setup(self):
        """Called to setup the experiment by finding the blue tube icon, setting profile counts and pressure, configuring the sort settings, and starting the profile.
        After profiling, some time is given to adjust the gates for the negative control. Then, the user will press enter to confirm they have the correct gates,
        and the automation software will take over by closing the sheet and duplicating the tube.

        !! This is assuming the user has ONLY set up gates and nothing else !!
        :raises: TypeError if the number of gates is not consistent with the number required. The error is handled internally.
        """
        
        log.info("Setting up automation software")
        curr_worksheet = self.c.find_and_center_click('BLUE_TUBE_ICON') #grab the blue tube icon before we start profiling
        self.c.set_profile_counts()
        self.c.change_sort_method()
        self.c.run_profile()
        self.c.return_to_git()
        log.info("Profile completed, allowing user to adjust gates.")
        input("Profile has been completed. Please adjust your gates accordingly, and then press enter when you are ready to start automation.")
        #check number of gates
        num_gates = self.c.read_num_gates()
        try:
            if num_gates == 4:
                log.info("Number of gates passes")
            else:
                raise TypeError
        except TypeError: #Will also raise if we get a non-integer value
            while True:
                confirmed = input("Software issue raised reading number of gates. Please double check that you have exactly FOUR gates under Gates and Statistics.\nOnce you have confirmed four gates, please type 'y':")
                if confirmed in ['y','Y']:
                    break
        self.c.close_sheet(False) 
        self.c._duplicate_tube(None, curr_worksheet, True)
        
    def experiment_continuation(self):
        """Called instead of experiment_setup for all runs of automation program
        when profiling cells is not necessary. This assumes that the first sort settings have been set
        and a new tube has been duplicated. When a previous experiment has been running, a sort setting
        must be present, and needs to be deleted.
        """
        
        self.c.find_and_center_click('SORT_SETTINGS_BTN')
        self.c._delete_previous_sort()
        self.c.find_and_center_click('CLOSE_BTN')

    def cancel_threads(self):
        """Cancels threads.
        """
        
        log.info("Cancelling all threads.")
        if self.temp_thread is not None:
            self.temp_thread.cancel()
            if self.temp_thread.is_alive():
                self.temp_thread.join()
        if self.agitation_thread is not None:
            self.agitation_thread.cancel()
            if self.agitation_thread.is_alive():
                self.agitation_thread.join()
        if self.error_check is not None:
            self.error_check.cancel()
            if self.error_check.is_alive():
                self.error_check.join()

    def done_protocol(self):
        """Called if sorting finishes or software stopped
        """
        
        log.info('Entered Done Protocol')
        self.cancel_threads()
        if self.interrupt:
            self.slk.sendMessage('FACS_stopped', self.user, self.no_slack)
        else:
            self.slk.sendMessage('FACS_complete', self.user, self.no_slack)
        with(self.arduino_call_lock):  # Makes sure this is the last arduino call
            self.hc.run_complete()
        log.info("Finished done protocol call")
        self.c.return_to_git


    ######################
    # Interrupt Calls    #
    ######################

    def start_keyboard_listener(self):
        """Start a non-blocking listener thread to pick up key strokes

        F5: pause, F6: resume, F7: stop,
        """
        
        listener = keyboard.GlobalHotKeys({
                '<F5>': self.on_activate_pause,
                '<F6>': self.on_activate_resume,
                '<F7>': self.on_activate_stop})
        listener.start()

    def on_activate_pause(self):
        """Called when F5 is pressed
        """

        log.info('Key pressed: \'F5\'')
        tstp = datetime.datetime.now()
        tpause = tstp.strftime("%Y-%m-%d-%H-%M-%S")
        fpause = f"{log_filepath}/{tpause}_pause"
        self.c.screenshot_state(fpause)
        self.slk.uploadFile(f"{fpause}.png", self.no_slack)
        self.slk.sendMessage('FACS_pause', self.user, self.no_slack)
        if self.arduino_call_lock.locked() is False:
            log.info('Pausing FACS Automation')
            self.pause_lock.acquire()
            if self.facs is not None:
                pProcess(self.facs.pid).suspend()
        else:
            log.info('Not is a state to pause')

    def on_activate_resume(self):
        """Called when F6 is pressed
        """

        log.info('Key pressed: \'F6\'')
        if self.arduino_call_lock.locked() is False:
            if self.pause_lock.locked() is True:
                log.info('Resuming FACS Automation')
                self.pause_lock.release()
                if self.facs is not None:
                    pProcess(self.facs.pid).resume()
                    self.slk.sendMessage('FACS_resume', self.user, self.no_slack)
            else:
                log.info('FACS Automation already resumed')
        else:
            log.info('Cannot resume while hardware is in motion. Press F6 once hardware has stopped to resume')

    def on_activate_stop(self):
        """Called when F7 is pressed
        """

        log.info('Key pressed: \'F7\'')
        if self.arduino_call_lock.locked() is False:
            log.info('Stopping FACS Automation')
            tstp = datetime.datetime.now()
            tpause = tstp.strftime("%Y-%m-%d-%H-%M-%S")
            fpause = f"{log_filepath}/{tpause}_pause"
            self.c.screenshot_state(fpause)
            self.slk.uploadFile(f"{fpause}.png", self.no_slack)
            self.interrupt = True
            self.cancel_threads()
            if self.agitation_event is not None:
                self.agitation_event.set() #If in the middle of a sorting run (will only occur when facs not None), then agitation will be an event -- no need to check if none
            if self.facs is not None:
                pProcess(self.facs.pid).kill()
            self.cleanup()
        else:
            log.info('System has already been stopped or was not in the middle of sorting')

    ####################
    # Running Sort     #
    ####################
    def run_sequence(self, exp_name: str, sample_data: Dict[str, List[str]]):
        """Runs the sequence of events to sort all samples from csv dataset. 
        Start the sequence of events to sort samples

        :param exp_name: Name of the experiment received from the user input
        :type exp_name: str
        :param sample_data: The dictionary of relevant data for each sample
        :type sample_data: Dict[str, List[str]]
        :raises: Any Zaber exception requires restart and reinitialization of Zaber connection
        """
        
        self.hc.run_setup(self.data_dict['Tube'][0])  # Agitate first tube before starting
        is_first = True
        for i in range(len(sample_data['Tube'])):
            self.remaining_tubes = sample_data['Tube'][i+1:]  # used to know motors with samples
            log.info('Sorting sample: {}'.format(sample_data['Name'][i]))
            log.info('From tube: {}'.format(sample_data['Tube'][i]))
            log.info('Into Well: {}'.format(sample_data['Well'][i]))
            self.slk.tubeStatusThread(sample_data['Tube'][i], self.slk_timestamp, self.no_slack, start=True)

            with(self.arduino_call_lock):  # moving hardware
                self.hc.turn_off_on_motors() # Extra insurance that all motors are off
                try:
                    self.hc.start_sort(sample_data['Tube'][i])  # Make sure tube isn't agitated while pickup
                except:
                    log.info('Zaber Exception')
                    self.slk.sendMessage('FACS_Zaber_error', self.user, self.no_slack)
                    self.hc.run_complete()
                    raise Exception
            
            self.agitation_event = Event()

            if self.env == 'prod':
                self.facs = mProcess(target=single_sort,args=(is_first, self.c, exp_name, sample_data['Name'][i], sample_data['Well'][i],self.agitation_event))  # running sort
            elif self.env == 'dev' or self.env == 'test':
                self.facs = mProcess(target=single_sort,args=(is_first, exp_name, sample_data['Name'][i], sample_data['Well'][i],self.agitation_event,self.env,))  # running sort
            self.facs.daemon = True

            self.facs.start()

            agitation_time = time()
            while True:
                elapsed_time = time() - agitation_time
                if elapsed_time > 360:
                    self.agitation_event.set()
                if self.agitation_event.is_set():
                    break
            try:
                next_tube = sample_data['Tube'][i+1]
                log.info(f"Event set to agitate next tube {next_tube}")
                self.schedule_next_agitation(sample_data['Tube'][i], next_tube)
            except IndexError:
                next_tube = None 

            self.facs.join()
            self.agitation_event = None
            self.facs = None # make the pid none when process finishes
            is_first = False
            if self.stop:
                break

            with(self.arduino_call_lock):  # moving hardware
                try:
                    self.hc.finish_sort(sample_data['Tube'][i])   
                except:
                    log.info('Zaber Exception')
                    self.slk.sendMessage('FACS_Zaber_error', self.user, self.no_slack)
                    self.cancel_threads()
                    self.hc.run_complete()
                    raise Exception
                    
            log.info('Completed sorting sample: {}'.format(sample_data['Name'][i]))
            self.slk.tubeStatusThread(sample_data['Tube'][i], self.slk_timestamp, self.no_slack, start=False)

    def schedule_next_agitation(self, curr_tube: int, next_tube: Optional[int]):
        """Calls the hardware controller function to agitate the next sample tube in queue
        
        :param curr_tube: tube currently being processed through the automation
        :type curr_tube: int
        :param next_tube: next tube in the list to be processed through the automation that needs to be shaken
        :type next_tube: int
        """
        
        with (self.arduino_call_lock):
            log.info(f"Starting 30 sec agitation for {next_tube}.")
            self.hc.start_sequential_agitation(curr_tube, next_tube)
            Timer(30, self.stop_agitation_thread, [next_tube]).start()


    ###################
    # Monitor Threads #
    ###################

    def run_temperature_thread(self):
        """A new thread is spawned every interval time to check the temperature data
        """

        self.temp_thread = Timer(self.hc.temp_variables['check_time']*60.0, 
                                self.run_temperature_thread)
        log.info("started new temp thread")
        with(self.pause_lock):  # only start the reading if protocol is not on pause
            log.info("started here")
            self.temp_thread.start()
        
        with(self.arduino_call_lock):
            error_msg = self.hc.temperature_data()
            log.info("got temperature msg")
        log.info("done")
    
    def run_agitation_thread(self):
        """A new thread is spawned every interval time to check the status of the 
        motors for the remaining samples and agitate the motors for 30 sec
        """

        self.agitation_thread = Timer(self.hc.agitation_interval*60.0,
                                    self.run_agitation_thread)
        with(self.pause_lock):  # only run interval agitation if protocol is not on pause
            self.agitation_thread.start()
        if self.first_agitation_call:  # makes sure the thread runs after the interval passed
            self.first_agitation_call = False
        else:
            log.info('Agitating remaining samples')
            if len(self.remaining_tubes) >9:
                first_set = self.remaining_tubes[:len(self.remaining_tubes)//2]
                second_set = self.remaining_tubes[len(self.remaining_tubes)//2:]
                total_set = [first_set, second_set]
            else:
                total_set = [self.remaining_tubes]

                for tubeset in total_set:
                    with(self.arduino_call_lock):
                        self.hc.agitate_multiple_motors(tubeset)
                    i = 0
                    while(i<30): # this thread agitates the motors for a 30 sec
                        sleep(1)
                        i+=1
                        if self.stop: # stop waiting if stop keyed in
                            break
                    if not self.stop: # all running tubes are already stopped if stop keyed in
                        with(self.arduino_call_lock):  # turns off all the agitated motors after 30 sec
                            self.hc.agitate_multiple_motors(tubeset, False)
                        log.info('Finished interval agitation of {}'.format(tubeset))
    
    def stop_agitation_thread(self, tube_no: int):
        """Called after 30 sec of starting the sequential agitation to stop it

        :param tube_no: tube to stop agitation
        :type tube_no: int
        """

        if not self.stop: # all running tubes are already stopped if stop keyed in
            with(self.arduino_call_lock):
                log.info("Ran agitation for tube {}".format(tube_no))
                self.hc.ac.toggle_motor(tube_no, False)

    def error_check_thread(self):
        """A new thread is spawned every interval time to check if an error has appeared
        """

        self.error_check = Timer(60, 
                                self.error_check_thread)
        with(self.pause_lock):  # only start the reading if protocol is not on pause
            if not self.error_flag:
                self.error_check.start()
        
        self.error_flag = self.c.error_check()
        
        if self.error_flag:
            log.critical("Error was found!")
            self.c.return_to_git()
            self.on_activate_pause()
            self.slk.sendMessage('FACS_error', self.user, self.no_slack)
        else:
            log.info("No error was found.")
    

    #########################
    # Convenience Functions #
    #########################

    def _rename_log_file(self, file_name):
        """Closes the open log file to rename it, and then reopens it for editing.

        Parameters
        ----------
        file_name : str
        The file name to change the log file to.
        """
        
        timestamp = datetime.datetime.now()
        tme = timestamp.strftime("%Y-%m-%d")
        log_filename = f"../../logs/hi_log"
        new_filename = f"../../logs/{file_name}_log"
        handlers = log.handlers[:]
        for handler in handlers:
            handler.close()
            log.removeHandler(handler)
        os.rename(log_filename, new_filename)
        new_handler = logging.FileHandler(new_filename, mode='a')
        log.addHandler(new_handler)
        log.info(f"Renaming log file from 'hi_log' to '{file_name}_log'")


if __name__ == "__main__":
        FACSAutomation(sys.argv[1])