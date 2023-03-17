#!/Users/samia.sama/Documents/FACS_Automation/venv/bin/python3.7
import logging
from multiprocessing import Event
import numpy as np
from pyautogui import typewrite, hotkey, press, moveTo, click, doubleClick
import sys
from threading import Timer
from time import sleep
from czfacsautomation.sorting import Controller, Gating
from czfacsautomation.sorting.controller import MockController


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s',"%H:%M:%S")
handler.setFormatter(formatter)
log.addHandler(handler)

class Sort():
    """Performs a single sort process

    ivar c: Used to acess all the methods of the controller class
    type c: Controller() object
    ivar is_first_profile: True - Assumes the new tube is already created
                and activated. Set to False after first loop
    type is_first_profile: bool
    ivar current_worksheet: The location of the current worksheet on the side panel
                of the SONY Software (x,y). Either a profiling or a sorting worksheet
    type current_worksheet: List[float]
    ivar fourth_gate_loc: Coordinates of the 4th gate on the worksheet
    type fourth_gate_loc: List[float]
    """

    def __init__(self, is_first, controller):
        """Setup controller and initiate instance variables
        
        :param is_first: whether the sample is the first sample to run
        :type is_first: bool
        :param controller: instance of the Controller class
        :type controller: type
        """

        self.c = controller
        #TODO variable wait time
        self.is_first = is_first # If it is the first sample (for not deleting a sort setting)
        self.current_worksheet = None
        self.fourth_gate_loc = None
        self.is_profiling = Event()
        self.eps_values = []

    def _prep(self):
        """Any preparation step
        """
        
        sleep(self.c.wait_times['long'])

    def _profiling(self, sort_name: str):
        """Duplicate tube, start sorting, record till stop condition

        :param sort_name: Name of the sample
        :type sort_name: str
        """
        
        log.info('Starting The Profiling Step')
        self.current_worksheet = self.c.find_and_center_click('BLUE_TUBE_ICON')
        self.c.rename_tube(sort_name, 'profile')
        log.info('Begin Profile')
        self.is_profiling.set()
        self.check_eps_thread()
        self.c.run_profile()
        self.is_profiling.clear()

    def _gating(self, exp_name: str, sample_name: str):
        """Extract gate data, draw custom gate, set new gate

        :param exp_name: Name of the experiment that is running 
        :type exp_name: str
        :param sample_name: Name of the sample
        :type sample_name: str
        :raises: error if gating fails to allow the user to adjust thegate and continue
        """
        
        self.is_profiling.clear()
        log.info('Start Gating')
        self.fourth_gate_loc = self.c.export_csv_and_close_sheet()
        log.info(self.c.file_name)
        log.info('Getting And Setting Gate')
        metadata, dataset = self.c.get_csv_metadata(exp_name)
        log.info(f"Dataset: {dataset}")
        gating = Gating(metadata, dataset)
        try:
            gating.gate()
        except:
            press('f5')
            log.critical('Gating Failed.')
            log.critical('Manually adjust the gate on the profile. Close the worksheet. Then resume the workflow by pressing F6.')
            log.critical('Check that the profile is selected for duplication.')          
        click(self.current_worksheet)  # to prepare to duplicate for sort
        log.info('Finished Gating')
        sleep(self.c.wait_times['long'])

    def _sorting(self, sort_name: str, target_well: str, event):
        """Duplicate tube, set sort settings, sort sample

        :param sort_name: Name of the sample to sort
        :type sort_name: str
        :param target_well: Alphanumeric well location
        :type target_well: str
        :param event: multithreading event for whether to agitate the sample tube
        :type event: type
        """

        log.info('Start Sorting')
        self.current_worksheet = self.c._duplicate_tube(sort_name, self.current_worksheet, False)
        timeout = self.analyze_eps()
        self.c.set_stop_condition(False)
        self.c._configure_sort_settings(target_well, self.is_first, timeout) # If it's the first sample, sort settings were configured in setup already
        log.info("Ready To Sort")
        self.c.find_and_center_click('LOAD_COLLECTION_BTN')
        sleep(self.c.wait_times['long'])
        sleep(self.c.wait_times['long'])
        log.info("Start Sort")
        self.c.wait_till_found('START_BTN')
        self.c.find_and_center_click('START_BTN')
        log.info('Waiting For Cells')
        # TODO: switch to checking eps bar
        sleep(self.c.wait_times['cells_appear'])
        log.info('Wait Till Recording Finishes')
        self.c.find_and_center_click('SORT_AND_RECORD_BTN')
        self.c._wait_till_record_ends(False)
        event.set()
        log.info(f"Event should be set: {event.is_set()}")
        log.info('Wait Till Sorting Finishes')
        sleep(self.c.wait_times['short'])
        self.c.wait_till_found('FINISH_BTN', True, max_time = timeout)
        self.c.read_sort_counts()
        self.c.find_and_center_click('FINISH_BTN')
        log.info('Finished Sorting')
        click(self.fourth_gate_loc[0], 
            self.fourth_gate_loc[1])  # need to reactivate worksheet by clicking safe spot
        sleep(self.c.wait_times['extended'])
        self.c.find_and_center_click('CLOSE_WORKSHEET')  # ensure too many tabs are not open
        sleep(self.c.wait_times['short'])
        self.c.find_and_center_click('YES_BTN')
        self.c._duplicate_tube(None, self.current_worksheet, False)

    def check_eps_thread(self):
        """A new thread is spawned every interval time to record the eps values during profiling.
        """
        
        log.info("Running EPS thread")
        if self.is_profiling.is_set():
            eps_thread = Timer(5, self.check_eps_thread) # create this only if we are in the middle of sorting
            eps_thread.start()
            eps = self.c.read_event_rate()
            log.info(f"EPS is {eps}")
            if eps is not None:
                log.info(f"Adding eps reading: {eps}")
                self.eps_values.append(eps)
            else:
                log.info("Read a nonsensical eps value, attempting read again.")

        else:
            # Stop spawning new threads
            log.info("Clearing EPS thread")
            return
    
    def analyze_eps(self) -> int:
        """Analyzes the recorded eps after profiling and changes the sample pressure.
        
        :return: The sample timeout for sorting based on the desired pressure for sorting
        :rtype: int
        """
        
        log.info("Analyzing eps...")
        eps_bins = self.c._gui_config["PRESSURE_LOOKUP_TABLE"]["ranges"]
        pressures = self.c._gui_config["PRESSURE_LOOKUP_TABLE"]["pressures"]
        timeouts = self.c._gui_config["PRESSURE_LOOKUP_TABLE"]["timeouts"]
        # If the range is between 0-200, we should let the user know? 
        # When we have equal frequencies, how should we handle that? --> we should take the max of the pressure
        self.eps_values = self.eps_values[5:]
        hist = np.histogram(self.eps_values, eps_bins)
        print(self.eps_values)
        idx = np.where(hist[0] == max(hist[0]))
        idx = max(idx)[0] # if there are two, we'll make a conservative estimate w/ the lesser EPS to raise the pressure
        event_rate_guess = hist[1][idx]
        pressure_idx = len(pressures) - idx - 1
        sample_pressure = pressures[pressure_idx]
        sample_timeout = timeouts[pressure_idx]
        log.info(f"Guessing an event rate of {event_rate_guess}. Setting pressure to {sample_pressure}")
        self.c.set_pressure(sample_pressure)
        log.info(f"Setting timeout to {sample_timeout}")
        return sample_timeout





class MockSort(Sort):
    def __init__(self):
        # Should edit the main sorting_automation to take a variable if mock, so we can do super.__init__(env='dev')
        # and it will set up the mock controller
        self.c = MockController()
        self.current_worksheet = None
        self.fourth_gate_loc = None

    def _prep(self):
        return

    def _profiling(self, sort_name: str):
        log.info("Starting profiling steps for {}".format(sort_name))
        self.c._duplicate_tube(sort_name, self.current_worksheet, True)
        log.info("Begin profile")
        log.info("Waiting for cells")
        sleep(1)
        log.info("Recording until stop condition is met")
        self._wait_till_record_ends()
        log.info("Finished profile")

    def _gating(self, exp_name: str, sort_name: str):
        log.info('Start gating for {}'.format(exp_name))
        sleep(3)
        log.info("Finished gating")

    def _sorting(self, sort_name: str, target_well: str,e):
        log.info("Starting sort {} on well {}".format(sort_name, target_well))

        sleep(1)
        self.c._duplicate_tube(sort_name, self.current_worksheet, False)
        self.c._configure_sort_settings(target_well)
        log.info("Ready to sort")
        sleep(1)
        log.info("Pressing button to start sort")
        sleep(1)
        log.info("Waiting for cells")
        sleep(2)
        log.info("Waiting until recording finishes")
        self._wait_till_record_ends()
        e.set()
        log.info(f"Event should be set: {e.is_set()}")
        log.info("Waiting until sorting finishes")
        sleep(1)
   
        log.info("Finished sorting")
        return

    def _duplicate_tube(self, sort_name: str, curr_worksheet, is_profiling: bool):
        log.info("Duplicating and activating new tube")
        sleep(3)
        return

    def _configure_sort_settings(self, target_well: str):
        log.info('Configure The Sort Settings')
        sleep(3)
        log.info('Finished configuring sort settings')
        return

    def _wait_till_record_ends(self):
        log.info("Waiting for record to end")
        sleep(2)
        log.info("Found the color")
        return