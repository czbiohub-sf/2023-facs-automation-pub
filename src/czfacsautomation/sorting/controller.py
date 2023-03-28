from json import load
import logging
from os import path, listdir, remove
from pandas import read_csv
from pkg_resources import Requirement, resource_filename
import pyautogui
from pyautogui import locateOnScreen, click, center, screenshot, pixelMatchesColor, typewrite, doubleClick, hotkey, scroll, moveTo, press, locateAllOnScreen
from pyperclip import copy, paste
import pytesseract
import sys
from time import sleep, time
from typing import Tuple, List

# Set log to terminal
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s',"%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
log.addHandler(handler)

# Set pyautogui failsafe to false
pyautogui.FAILSAFE = False


class Controller():
    """Contains wrapper methods to pyautogui calls and connects to external files

    :ivar img_file_loc: The directory holding the image snippets 
    :type img_file_loc: str
    :ivar _gui_config: Contains the name of the image file and other config parameters 
    :type gate_coords: Dict{k:v}, k = image identifier, v = config parameters
    :ivar _multiple_use_btns: To reduce resource use, buttons that are clicked multiple
                times are found on initialization and the coordiates are stored for 
                rg match and clicks
    :type _multiple_use_btns: Dict{k:v}, k = button identifier, v = center location
    """

    def __init__(self, find_btns = True):
        """Retrieves data from json config file and initiates instance variables
        
        :param find_btns: determines whether the start, record, and stop buttons should be found
        :type find_btns: bool
        """
        
        self.img_file_loc = resource_filename(Requirement.parse("czfacsautomation"), "config/gui_snippets/")
        gui_config_file = resource_filename(Requirement.parse("czfacsautomation"), "config/gui_config.json")
        with open(gui_config_file, 'r') as f:
                self._gui_config = load(f)
        self.image_flag = 0
        if find_btns:
            self._multiple_use_btns = {
                "START_BTN" : self.find_on_screen('START_BTN'),
                "RECORD_BTN": self.find_on_screen('RECORD_BTN'),
                "STOP_BTN" : self.find_on_screen('STOP_BTN')
            }
        else:
            self._multiple_use_btns = {}
        self.wait_times = self._gui_config['WAIT_TIMES']
        self.sort_count = self._gui_config['SORT_COUNT']['count']
        self.sort_timeout = self._gui_config['SORT_TIMEOUT']['seconds']

    ####################################
    # Common PyAutoGui Wrapper Methods #
    ####################################

    def loc_all_on_screen(self, image_name: str, check_none=False) -> List[float]:
        """Locates where a specific image is found on the screen and returns its position
        using the pyautoGUI function
        
        :param image_name: The image identifier in the JSON file
        :type image_name: str
        :param check_none: True: Initiates call to _image_not_found_handler()
                    if image is not found on screen, False: Ignores not found 
                    (used when waiting till found)
        :type check_none: bool
        :raises TypeError: Raised if image is not found and the appropriate handler
                    is called
        :raises OSError: Raised if the image file is not found in the image directory,
                    raises the not found handler to ask user to retry
        :return: List[x, y, w, h]: x = x coordinate of the top left of image,
                    y = y of top left, w = width of image, h = height of the image
        :rtype: List[float]
        """
        
        loc = None
        try:
            try:
                img_file = '{}{}'.format(self.img_file_loc, self._gui_config[image_name]['name'])
                loc = locateAllOnScreen(img_file, confidence = 0.9)
            except OSError:
                log.critical('{}: IMAGE FILE NOT FOUND IN FOLDER'.format(img_file))
                self._image_not_found_handler(image_name)
            if check_none and loc is None:
                raise TypeError
        except TypeError:
            self._image_not_found_handler(image_name)
            loc = self.find_on_screen(image_name, check_none)  # called again if retry selected
            self.image_flag = 0 # resets flag if it is successful
        return loc

    def _image_not_found_handler(self, image_name: str):
        """Waits 2s then retries, unless paused

        The current handler is mainly designed for debugging and to trace
        unexpected reasons for not locating the image. The retry enables 
        the user to fix the issue before continuing from the same step.
        Once there are only a few image not found cases, the handler can
        be switched to slack RA when image not found.

        :param image_name: The image identifier in the JSON file
        :type image_name: str
        """
        
        log.critical('{}: NOT FOUND ON SCREEN'.format(image_name))
        if self.image_flag <= 5:
            log.critical('Will retry again in 2s')
            log.critical('Press F5 to pause or F7 to stop')
            sleep(2)
            self.image_flag += 1
        
        else:
            self.image_flag = 0
            press('f5')
            
    def find_and_center_click(self, image_name: str) -> Tuple[float, float]:
        """Finds the image and clicks the center location on the screen

        :param image_name: The image identifier in the JSON file
        :type image_name: str
        :raises KeyError: The dictionary containing high use buttons are first
                parsed before doing image recognition
        :return: The coordinates of the center of the image found on screen
        :rtype: Tuple[float, float]
        """

        try:
            image_loc = self._multiple_use_btns[image_name]
            center_loc = center(image_loc)
        except KeyError:
            center_loc = center(self.find_on_screen(image_name))
        click(center_loc)
        sleep(self.wait_times['short'])
        return center_loc
        
    def find_on_screen(self, image_name: str, check_none: bool=True) -> List[float]:
        """Locates an image on the screen and returns center location

        :param image_name: The image identifier in the JSON file
        :type image_name: str
        :param check_none: True: Initiates call to _image_not_found_handler()
                    if image is not found on screen, False: Ignores not found 
                    (used when waiting till found), defaults to True
        :type check_none: bool, optional
        :raises TypeError: Raised if image is not found and the appropriate handler
                    is called
        :raises OSError: Raised if the image file is not found in the image directory,
                    raises the not found handler to ask user to retry
        :return: List[x, y, w, h]: x = x coordinate of the top left of image,
                    y = y of top left, w = width of image, h = height of the image
        :rtype: List[float]
        """
        
        loc = None
        try:
            try:
                img_file = '{}{}'.format(self.img_file_loc, self._gui_config[image_name]['name'])
                loc = locateOnScreen(img_file, confidence = 0.9)
            except OSError:
                log.critical('{}: IMAGE FILE NOT FOUND IN FOLDER'.format(img_file))
                self._image_not_found_handler(image_name)
            if check_none and loc is None:
                raise TypeError
        except TypeError:
            self._image_not_found_handler(image_name)
            loc = self.find_on_screen(image_name, check_none)  # called again if retry selected
            self.image_flag = 0 # resets flag if it is successful
        return loc

    def find_all_on_screen(self, image_name: str, check_none: bool=True) -> List[float]:
        """Locates an image on the screen and returns center location

        :param image_name: The image identifier in the JSON file
        :type image_name: str
        :param check_none: True: Initiates call to _image_not_found_handler()
                    if image is not found on screen, False: Ignores not found 
                    (used when waiting till found), defaults to True
        :type check_none: bool, optional
        :raises TypeError: Raised if image is not found and the appropriate handler
                    is called
        :raises OSError: Raised if the image file is not found in the image directory,
                    raises the not found handler to ask user to retry
        :return: List[x, y, w, h]: x = x coordinate of the top left of image,
                    y = y of top left, w = width of image, h = height of the image
        :rtype: List[float]
        """
        
        loc = None
        try:
            try:
                img_file = '{}{}'.format(self.img_file_loc, self._gui_config[image_name]['name'])
                loc = locateAllOnScreen(img_file, confidence = 0.9)
            except OSError:
                log.critical('{}: IMAGE FILE NOT FOUND IN FOLDER'.format(img_file))
                self._image_not_found_handler(image_name)
            if check_none and loc is None:
                raise TypeError
        except TypeError:
            self._image_not_found_handler(image_name)
            loc = self.find_all_on_screen(image_name, check_none)  # called again if retry selected
            self.image_flag = 0 # resets flag if it is successful
        return loc
    
    def scroll_till_found(self, image_name: str, step_size: int=1, tries: int=200) -> List[float]:
        """Scrolls  a few increments, tries to find the image, if not found, will scroll again.
        Scroll up or down based on step size (up > 0, down < 0).

        :param image_name: The image identifier in the JSON file
        :type image_name: str
        :param step_size: Step size to scroll, amount of "clicks"
        :type step_size: int
        :param tries: Attempts to find the image
        :type tries: int
        :return: List[x, y, w, h]: x = x coordinate of the top left of image,
                    y = y of top left, w = width of image, h = height of the image
        :rtype: List[float]
        """
        
        count = 0
        loc = None
        while count < tries:
            loc = self.find_on_screen(image_name, False)
            if loc is not None:
                break
            else:
                scroll(step_size)
                count += 1
        return loc

    def wait_till_found(self, image_name: str, search_img: bool=False, max_time: int=60):
        """Loops by the extended wait time to either find an rgb match or an image on screen

        The rgb match is used to determine if a button is active again 
        (i.e. for start or record button to change colors). Locating image
        on screen is used to wait for pop ups (i.e. when cell count is reached)

        :param image_name: The image identifier in the JSON file
        :type image_name: str
        :param search_img: True: find the image on screen, False: do a rgb match,
                    defaults to False
        :type search_img: bool, optional
        :param max_time: The time to wait for the image icon to appear
        :type max_time: int
        """

        count = 0
        log.info('Entered Wait Till Found with Image {} and max_time {}'.format(image_name, max_time))
        while True:
            if search_img:
                img = self.find_on_screen(image_name, False)
                if img is not None:  # Found image on screen
                    log.info('Wait Till Found Count: {}'.format(count))
                    break
            else:
                if self._is_btn_active(image_name):  # rgb matched
                    log.info('Wait Till Found Count: {}'.format(count))
                    break
            if count >= max_time / self.wait_times['extended']:
                log.critical('Script Timed Out')
                self.image_flag = 6 #used to pass through the condition flag in _image_not_found_handler
                self._image_not_found_handler(image_name)
                count = 0  # Restarts wait timer if retry option chosen in handler
            count += 1
            sleep(self.wait_times['extended'])

    def _get_rgb(self, img_name):
        """Prints the rgb of a image stored in the multiple use dictionary
        
        Used to save the rgb parameter in the json config file

        :param img_name: The image identifier in the multiple use dictionary
        :type img_name: str
        """
        
        center_pos = center(self._multiple_use_btns[img_name])
        tuple_ex = (int(center_pos[0]), int(center_pos[1]))
        print(screenshot().getpixel(tuple_ex))

    def _is_btn_active(self, img_name: str) -> bool:
        """Matches the rgb color to the color saved in the json file

        :param img_name: Image identifier in the multiple use dictionary
        :type img_name: str
        :raises KeyError: Program outputs error if rgb field not found in json file
        :raises KeyError: Logs error button key not found in the multiple use dictionary
        :return: True: Color matches
        :rtype: bool
        """

        try:
            if img_name in self._multiple_use_btns:
                center_pos = center(self._multiple_use_btns[img_name])
            else:
                pos = self.find_on_screen(img_name)
                center_pos = center(pos)
                if img_name == 'DUPLICATE_BTN':
                    # Duplicate btn isn't exactly centered, so it needs to be shifted
                    center_pos = center_pos[0] + 5, center_pos[1] + 5
            try:
                return pixelMatchesColor(int(center_pos[0]), int(center_pos[1]), 
                                        self._gui_config[img_name]['rgb'], tolerance = 10)
            except KeyError:
                log.error('rgb field not found in json file, please add before continuing')
                quit() # TODO can't just quit
        except KeyError:
            log.error('The button to use for rgb matching is not found in the dictionary.')
            quit()

    ###########################
    # GUI Interacting Methods #
    ###########################
    def export_csv_and_close_sheet(self, loc=None, scraper=False) -> Tuple[float, float]:
        """Exports the data from the Sony GUI
        
        :param loc: filepath for saving the data
        :type loc: str
        :param scraper: whether the export is during data scraping or active sorting
        :type scraper: bool
        :return: The location of the fourth gate
        :rtype: Tuple[float, float]
        """
        
        log.info("Exporting CSV and then closing sheet")
        self.clear_csv_dir()  # Ensure only 1 file at a time in dir
        fourth_gate_loc = self.click_fourth_graph()
        sleep(self.wait_times['short']) # Accounting for cases when it will flash black and then go back to gray
        self.wait_till_found('EXPORT_CSV_BTN')
        sleep(self.wait_times['short'])
        self.find_and_center_click('EXPORT_CSV_BTN')
        self.find_and_center_click('OUTPUT_PATH')
        self.rename_csv(loc)
        self.find_and_center_click('SAVE_CSV')
        self.find_and_center_click('EXPORT_BTN')
        sleep(self.wait_times['long'])  # wait to finish export
        self.wait_till_found('OK_BTN', True)
        self.find_and_center_click('OK_BTN')
        self.find_and_center_click('CLOSE_BTN')
        self.close_sheet(scraper)
        return fourth_gate_loc

    def close_sheet(self, scraper):
        """Closs the active worksheet in the Sony GUI
        The sort scraper borrows some functionality from the controller to export data; however, if it is scraping, the 'YES_BTN'
        is not needed since the tubes are no longer active.
        
        :param scraper: whether the export is during data scraping or active sorting
        :type scraper: bool
        """
        
        if not scraper:
            sleep(self.wait_times['short'])
        self.find_and_center_click('CLOSE_WORKSHEET')  # required for GateVertexTool
        sleep(self.wait_times['short'])
        if not scraper:
            self.find_and_center_click('YES_BTN')
        sleep(self.wait_times['long'])  # wait to finish closing


    def click_fourth_graph(self) -> Tuple[float, float]:
        """Click the 4th graph in preparation for data export

        The 4th graph is found by finding the 'All Events' graph (1st) and
        then offsetting from there. The 'All Events' graph can either be 
        in a selected state or a not selected state.

        :return: The location of the fourth gate
        :rtype: Tuple[float, float]
        """

        offset = self._gui_config['FOURTH_GRAPH']['offset']
        loc = self.find_on_screen('ALL_EVENTS_UNSEL', False)
        if loc is None:
            loc = self.find_on_screen('ALL_EVENTS_SEL')
        click(loc[0]+offset, loc[1]+offset)
        return [loc[0]+offset, loc[1]+offset]
      
    def rename_csv(self, loc=None):
        """Renmes the exported csv file to contain the required information to use with the GateVertexTool
        
        :param loc: filepath for saving the data
        :type loc: str
        """
        
        path = self.find_on_screen('FILEPATH')
        # Copies current title name to a variable so we can parse
        offset = self._gui_config['FILEPATH']['y_offset']
        click(path[0], path[1]+offset)
        hotkey('ctrl','a')
        hotkey('ctrl','c')
        sleep(.1)
        curr_title = paste()
        parsed = curr_title.split("_")
        sample_name = parsed[3]
        group_name = parsed[2]
        expt_name = parsed[1]
        user_name = parsed[0]
        self.file_name = [user_name, expt_name, group_name, sample_name]
        if loc is None:
            # Set it to the default, which should be for all profile data exports
            loc = (self._gui_config['GATE_CSV_DIR']['location']).replace("\\","\\")
        filename = '{}\{}_{}_{}_{}'.format(loc, self.file_name[0], self.file_name[1], self.file_name[2], self.file_name[3])
        log.info("Setting file name as: {}".format(self.file_name))
        click(path[0], path[1]+offset)
        hotkey('ctrl','a')
        copy(filename)
        hotkey('ctrl','v')
        log.info("filename is: {}".format(filename))
   
    def get_csv_metadata(self, exp_name: str
                        ) -> Tuple[List[str], List[List[float]]]:
        """Return the experiment metadata and datapoints

        The experiment metadata is used by the GateVertexTool to set and get 
        gete. The datapoints are used to create a custom gate

        :param exp_name: Name of the experiment
        :type exp_name: str
        :return: Tuple[a, b], a = metadata of the experiment
            [<user>, <exp_name>, <group_name>, <sample_name>]
            b = Scatter plot data [<x coordinates>, <y coordinates>] 
        :rtype: Tuple[List[str], List[List[float]]]
        """

        gate_dir = self._gui_config['GATE_CSV_DIR']['location']
        csv_file_name = listdir(gate_dir)[0]
        if csv_file_name is None:
            log.error('Gate dataset is not found in {}'.format(gate_dir))
            log.error('Please ensure the look up directory matches the export location')
            # TODO: retry get csv metadata
        file_name = '{0}\\{1}'.format(gate_dir, csv_file_name)
        log.info('Opening file: {}'.format(file_name))
        x_name = self._gui_config['DATASET']['x']
        y_name = self._gui_config['DATASET']['y']
        cluster = read_csv(file_name, usecols=[x_name, y_name])
        log.info(self.file_name)
        inp = self.file_name
        return inp, [cluster[x_name], cluster[y_name]]

    def clear_csv_dir(self):
        """The dataset directory is cleared before saving a new file

        The directory is cleared to make sure there is only 1 file at a 
        time, to know the current sample being sorted
        """

        gate_dir = self._gui_config['GATE_CSV_DIR']['location']
        filelist = [ f for f in listdir(gate_dir)]
        for f in filelist:
            remove(path.join(gate_dir, f))

    def _configure_sort_settings(self, target_well: str, first_sort=False, sort_timeout=None):
        """Make all the clicks to setup the sort parameters

        :param target_well: The well to sort into
        :type target_well: str
        :param first_sort: Whether or not this is the first sort / if there is a sort setting to delete. Default False.
        :type first_sort: bool
        :param sort_timeout: sort setting to stop the sort after the time elapsed
        :type sort_timeout: int
        """

        log.info('Configure The Sort Settings')
        self.find_and_center_click('SORT_SETTINGS_BTN')
        self.select_target_well(target_well)
        coord = self.find_title_click_dropdown('Sort_Gate')
        sleep(self.wait_times['short'])
        self.select_dropdown_option('Sort_Gate', coord)
        coord = self.find_title_click_dropdown('Sort_Mode')
        sleep(self.wait_times['short'])
        self.select_dropdown_option('Ultra_Purity', coord)
        self.find_title_click_dropdown('Stop_Count')
        sleep(self.wait_times['short'])
        hotkey('ctrl', 'a')
        hotkey('ctrl', 'x')
        typewrite('{}'.format(self.sort_count))
        # sort timeout
        self.find_title_click_dropdown('SORT_TIMEOUT_BTN')
        sleep(self.wait_times['short'])
        hotkey('ctrl', 'a')
        hotkey('ctrl', 'x')
        if sort_timeout == None:
            typewrite('{}'.format(self.sort_timeout))
        else:
            typewrite('{}'.format(sort_timeout))


        log.info('Parameters Are Set')
        self.find_and_center_click('ADD_BTN')

        if not first_sort:
            self._delete_previous_sort()
            
        self.find_and_center_click('CLOSE_BTN')
        sleep(self.wait_times['short'])
        log.info('Finished configuring sort settings')
    
    def _delete_previous_sort(self):
        """Deletes the prior sort settings
        """
        
        log.info('Delete Previous Sort')
        header_loc = self.find_on_screen('SortID_Header')
        click(header_loc[0], header_loc[1] + header_loc[3] + 5)
        self.find_and_center_click('REMOVE_BTN')
        sleep(self.wait_times['short'])

    def _duplicate_tube(self, sort_name: str, curr_worksheet, is_profiling: bool):
        """Click and activate and rename new tube

        If it is the first profile, then assume that the current tube
        is ready for sorting and only rename the tube. Otherwise duplicate
        and activate new tube.

        :param sort_name: Name of the sample sorted
        :type sort_name: str
        :param curr_worksheet: Location of the last blue tube icon (current worksheet) -- if None, clicks where the mouse cursor
        :type curr_worksheet: array-like or None
        :param is_profiling: True: profiling step, False: sorting step
        :type is_profiling: bool

        :rparam curr_worksheet: The coords of the current worksheet (will be updated to the new tube)
        :rtype curr_worksheet: array-like
        """

        name = 'profile' if is_profiling else 'sort'
        click(curr_worksheet)
        self.wait_till_found('DUPLICATE_BTN')
        self.find_and_center_click('DUPLICATE_BTN')
        sleep(self.wait_times['long'])
        self.wait_till_found('ASSIGN_BTN')
        self.find_and_center_click('ASSIGN_BTN')
        sleep(self.wait_times['long'])
        curr_worksheet = self.find_and_center_click('BLUE_TUBE_ICON')
        if sort_name != None:
            self.rename_tube(sort_name, name)
        return curr_worksheet

    def rename_tube(self, sort_name, name):
        """Renames the active sorting sample tube
        
        :param sort_name: Name of the sample sorted
        :type sort_name: str
        :param name: added name component as to whether a profile or sort
        :type name: str
        """
        
        tube = '{} {}'.format(sort_name, name)
        press('f2')
        sleep(self.wait_times['short'])
        copy(tube)
        hotkey('ctrl','v')
        press('enter')
    
    def set_profile_counts(self):
        """Sets profile counts to specified variable in the gui_config file.
        """
        
        counts = self._gui_config['PROFILE_COUNT']['count']
        log.info(f"Setting stop count for profiling to {counts} events.")
        self.find_title_click_dropdown('STOP_VALUE')
        sleep(self.wait_times['short'])
        hotkey('ctrl', 'a')
        hotkey('ctrl', 'x')
        typewrite('{}'.format(counts))
        press('enter')
    
    def set_pressure(self, pressure=None):
        """Sets sample pressure to specified variable in the gui_config variable. Recommended value is between 4-7.
        
        :param pressure: the pressure setting to select in the Sony GUI
        :type pressure: int
        """
        
        if pressure == None:
            pressure = self._gui_config['SAMPLE_PRESSURE']['number']
        log.info(f"Setting sample pressure to {pressure}.")
        coord = self.find_title_click_dropdown('SAMPLE_PRESSURE_IMG')
        sleep(self.wait_times['short'])
        y_loc = int(self._gui_config['SAMPLE_PRESSURE_IMG']['1_offset']) - (self._gui_config['SAMPLE_PRESSURE_IMG']['spacing'] * (int(pressure) - 1))
        coord[1] = coord[1] + y_loc
        click(coord)
    
    def set_stop_condition(self, is_profiling: bool):
        """Sets the data acqusition stop condition based on whether it is a profile or sort
        
        :param is_profiling: whether the data acquisition is a profile or sort
        :type is_profiling: bool
        """
        
        coord = self.find_title_click_dropdown('STOP_CONDITION')
        if is_profiling:
            y_loc = self._gui_config['STOP_CONDITION']['event_count_offset']
        else:
            y_loc = self._gui_config['STOP_CONDITION']['none_offset']    
        coord[1] = coord[1] + y_loc
        sleep(self.wait_times['short'])
        click(coord)
        log.info(f"Set sample data acquisition stop condition.")
    
    def change_sort_method(self):
        """Changes sort method from the default ( 2 Way Tubes ) to 96 Well Plate
        """
        
        coord = self.find_title_click_dropdown("SORT_METHOD")
        self.find_and_center_click("96wp")
        #self.select_dropdown_option("SORT_METHOD", coord)
    
    def scroll_experiment_bar(self, img_name: str, step: int=1, up: bool=True) -> List[float]:
        """Scrolls up or down the experiment bar.
        
        :param img_name: JSON identifier of the image to be looking for. Can use the blue tube icon w/ offset to find experiment names.
        :type img_name: str
        :param step: step size to scroll, 1 "click" is equivalent to 2 rows in the experiment bar
        :type step: int
        :param up: True, defaults to scrolling up
        :type up: bool
        :return: List[x, y, w, h]: x = x coordinate of the top left of image,
                    y = y of top left, w = width of image, h = height of the image
        :rtype: List[float]
        """
        
        # move cursor over experiment bar
        # Start by trying to find the image from the get-go
        coord = self.find_on_screen(img_name,False)
        if coord is None:
            # It's not on the current screen, keep scrolling
            coord = self.find_on_screen("EXPERIMENT_BAR")
            coord = (coord[0]+50,coord[1]+100)
            moveTo(coord)
            # Scroll until the image is found
            if not up:
                step = -1 * step
            coord = self.scroll_till_found(img_name, step)
            if coord is None:
                log.critical(f"Could not find {img_name}!")
        return coord
    
    def find_bottom_experiment_bar(self) -> List[float]:
        """This is under the assumption that we either find a blue tube icon, or there are enough tubes to scroll down.
        
        :return: List[x, y, w, h]: x = x coordinate of the top left of image,
                    y = y of top left, w = width of image, h = height of the image
        :rtype: List[float]
        """
        
        coord = self.find_on_screen("BLUE_TUBE_ICON", False)
        if coord is None: #blue tube icon wasn't found, hopefully it's at the bottom of the scroll bar
            coord = self.find_on_screen("SCROLL_BAR",False)
            if coord is not None: #a scroll bar exists!
                self.scroll_experiment_bar("SCROLL_BAR_BOTTOM", up=False)
            else:
                log.info("Bottom of the experiment bar couldn't be found!")
        return coord
            
    def return_to_git(self):
        """Clicks on the icon to open the git bash terminal window
        """
        
        self.find_and_center_click("TERMINAL")

    def run_profile(self):
        """Control of the Sony GUI to setup and start a profile of a sample
        """
        
        self.set_stop_condition(True)
        self.set_pressure()
        self.wait_till_found('START_BTN')
        self.find_and_center_click('START_BTN')
        sleep(self.wait_times['long'])
        log.info('Waiting For Cells')
        # TODO: switch to checking eps bar
        sleep(self.wait_times['cells_appear'])
        log.info('Recording Till Stop Condition Met')
        self.find_and_center_click('RECORD_BTN')
        self._wait_till_record_ends(True)
        self.find_and_center_click('STOP_BTN')
        sleep(self.wait_times['long'])
        log.info('Finished Profile')

    def _wait_till_record_ends(self, is_profile: bool):
        """Wrapper method used for waiting till recording finishes
        
        :param is_profile: whether the data acquisition is a profile or sort
        :type is_profile: bool
        """
        
        moveTo(100, 150)  # move the mouse away from the btn for rgb detection
        self.wait_till_found('RECORD_BTN', max_time = self.sort_timeout)
        log.info('Found the color')
        sleep(self.wait_times['short'])
        error = self.error_check()
        if is_profile and not (error):
            self.find_and_center_click('OK_BTN')
        # otherwise, we do nothing and wait for the error check thread to pick it up

    def error_check(self) -> List[float]:
        """Checks if an error flag icon is on the screen
        
        :return: List[x, y, w, h]: x = x coordinate of the top left of image,
                    y = y of top left, w = width of image, h = height of the image
        :rtype: List[float]     
        """
        
        found_error = self.find_on_screen("ERROR_MSG", False)
        sample_empty = self.find_on_screen("EMPTY_ERROR", False)
        error = found_error or sample_empty
        return error
        
    def find_sort_data(self, loc) -> str:
        """Clicks on the locations where sorts are to export data
        
        :param loc: coordinates of where to click for the sorted sample
        :type loc: List[float]
        :return: name of sample 
        :rtype: str
        """
        
        # Get the name of the sort
        click(loc)
        press('f2')
        sleep(0.1)
        hotkey('ctrl','a')
        hotkey('ctrl','c')
        press('enter')
        tube_name = paste()
        name_idx = tube_name.find(" sort")
        tube_name = tube_name[:name_idx]
        return tube_name

    def screenshot_last_sort(self, folder, loc):
        """Takes a screenshot of the last sort found
        
        :param folder: the filepath to use to save the image
        :type folder: str
        :param loc: the location where to take the screenshot (only a portion of the screen)
        :type loc: List[float]
        """
        
        screenshot(f"{folder}/last_sort.png",region=(loc[0]-220,loc[1],loc[2]+100,loc[3]))
        
    def screenshot_state(self, file):
        """Take a screenshot of the current state
        
        :param file: the file name and path for storing the image
        :type file: str
        """
        
        log.info('Taking a screenshot')
        screenshot(f"{file}.png")

    def export_sort_data(self, tube_name, loc):
        """Takes a screenshot of the fourth graph, used with the data scraping
        
        :param tube_name: The sample / tube name for naming conventions.
        :type tube_name: str
        :param loc: file path location of where to save the data.
        :type loc: str
        """
        
        doubleClick() # should already be in place
        # Screenshot the data
        # Click out to deselect gate
        sleep(4)
        click((1500,700,2,2))
        loc = f"{loc}/{tube_name}.png"
        graph = screenshot(region=(375,170,700,700))
        graph.save(loc)
        # Export the data
        fourth_graph_loc = self.click_fourth_graph()
        #graph_region = (fourth_graph_loc[0]-110,fourth_graph_loc[1]-65,335,330)


    ###############################
    # Sort Configurations Methods #
    ###############################

    def find_title_click_dropdown(self, title_name: str) -> float:
        """Finds the image of the title and clicks center left to activate dropdown

        The image axis is in the top left corner. With x increasing towards the right
        and y increasing downwards

        :param title_name: Identifier of the image to locate on screen
        :type title_name: str
        :return: The x,y location of the dropdown menu
        :rtype: List[float]
        """

        title_location = self.find_on_screen(title_name)
        x_loc = title_location[0] + title_location[2] + 60  # reach dropdown menu
        y_loc = title_location[1] + (title_location[3]/2)  # center of title
        click(x_loc, y_loc)
        return [x_loc, y_loc]

    def select_dropdown_option(self, option_title: str, start_loc: List[float]):
        """Clicks the drop down option based on the offset value from dropdown menu

        :param option_title: The identifier of the option on the json file
        :type option_title: str
        :param start_loc: The x,y coordinates of the dropdown menu
        :type start_loc: List[float]
        """
        
        click(start_loc[0], self._gui_config[option_title]['y_offset']+start_loc[1])

    def select_target_well(self, target_well: str):
        """Clicks on the desired target well

        :param target_well: The alphanumeric well to sort into (i.e. A11, B12)
        :type target_well: str
        """
        
        img_corners = self.find_on_screen('TOP_CORNER_WELL')
        row_letter = target_well[0].lower()
        col_num = target_well[1:]
        offset = self._gui_config['TOP_CORNER_WELL']['offset']
        x_desired = img_corners[0] + (int(col_num)*offset)
        y_desired = img_corners[1] + (ord(row_letter)-ord('a'))*offset
        click(x_desired, y_desired)


    ###############################
    #  Text Recognition Methods   #
    ###############################
    def read_text(self,img_name, offset=[0,0,0,0]) -> str:
        """Wrapper method to find an image on screen and read the text from it.

        :param img_name: The key of the image to find
        :type img_name: str
        :param offset: An offset from the image to use. Default [0,0,0,0]. [left, top, width, height]
        :type offset: list
        :return: The interpreted text. Error checking must be done on an individual basis.
        :rtype: str
        """
        
        img_loc = self.find_on_screen(img_name)
        loc = [sum(x) for x in zip(img_loc,offset)]
        img_found = screenshot(region=loc)
        strng = pytesseract.image_to_string(img_found)
        strng_end = strng.find('/n')
        return strng[:strng_end][:-1] #-1 eliminates the newline at the end 
    
    def read_sort_counts(self) -> str:
        """Used to read the counts text in the Sony GUI
        
        :raises TypeError: When no text value is read from the counts
        :return: The counts read on the screen
        :rtype: str
        """
        
        try:
            counts = self.read_text('COUNTS',offset=(90,0,85,0))
            if counts == '':
                raise TypeError
            log.info(f"Final counts read was: {counts}")
        except TypeError:
            log.info("Error in reading counts.")
        return counts
    
    def read_experiment_name(self) -> str:
        """Used to read the experiment name text in the Sony GUI
        
        :raises TypeError: When no text value is read from the experiment name
        :return: The experiment name in the Sony GUI read on the screen
        :rtype: str
        """
        
        try:
            self.find_and_center_click('EXPERIMENT_ICON')
            press('f2')
            sleep(self.wait_times['short'])
            hotkey('ctrl','a')
            hotkey('ctrl','c')
            press('enter')
            sleep(.1)
            experiment_name = paste()
            if experiment_name == '':
                raise TypeError
        except TypeError:
            log.info("Software errored reading experiment name.")
        return experiment_name
    
    def read_num_gates(self) -> int:
        """Reads the number of gates based on the rows in "Gates and Statistics"
        No try and except, since this is used in facs_automation.py -- if it reads incorrect, the whole program should quit. 
        Because this is prone to OCR error, however, we will ask the user to double check and restart if necessary.
        
        :raises TypeError: When the text value is nonsensical
        :return: The number of gates in the gate tree
        :rtype: int
        """
        
        gates = self.read_text("NUM_GATES",offset=[0,20,-20,200])
        try:
            num_gates = len(gates.split("\n")) - 2 # 2 extra numbers due to 'Name' and 'All Events'
        except TypeError:
            log.info("Returned nonsensical value.")
            return 0
        return num_gates

    def read_event_rate(self) -> int:
        """Reads the event rate (eps). The screenshot must include 'eps' for the OCR to work well!

        :raises TypeError: When the text value is nonsensica
        :return: The event rate read from the screen
        :rtype: int
        """
        
        read = self.read_text("EVENT_RATE",offset=[60,0,75,0])
        try:
            lst = read.split(" ") #will result in [string_num, eps]
            num = lst[0]
            idx = num.find(",")
            if idx != -1:
                num = num[:idx]+num[idx+1:]
            return int(num)
        except TypeError: # i imagine this is the most likely error to be raised if we get a nonsensical value
            return None


        

class MockController(Controller):
    def __init__(self):
        super().__init__()

    def find_and_center_click(self, image_name: str) -> Tuple[float, float]:
        log.info("Finding and clicking center")
        sleep(2)
        return (5.0,5.0)

    def find_on_screen(self, image_name: str, check_none: bool=True) -> List[float]:
        log.info("Finding {} on screen".format(image_name))
        sleep(2)
        loc = [1.0,1.0,5.0,5.0]
        return loc

    def wait_till_found(self, image_name: str, search_img: bool=False):
        log.info("Waiting until found")
        sleep(3)
        return

    def _is_btn_active(self, img_name: str) -> bool:
        log.info("Checking if button is active")
        sleep(3)
        return True

    def click_fourth_graph(self) -> Tuple[float, float]:
        sleep(2)
        return [2.0,2.0]

    def get_csv_metadata(self, exp_name: str):
        gate_dir = self._gui_config['GATE_CSV_DIR']['location']
        csv_file_name = listdir(gate_dir)[0]
        if csv_file_name is None:
            log.error('Gate dataset is not found in {}'.format(gate_dir))
            log.error('Please ensure the look up directory matches the export location')
            # TODO: retry get csv metadata
        file_name = '{0}\\{1}'.format(gate_dir, csv_file_name)
        log.info('Opening file: {}'.format(file_name))
        x_name = self._gui_config['DATASET']['x']
        y_name = self._gui_config['DATASET']['y']
        cluster = read_csv(file_name, usecols=[x_name, y_name])
        metadata = csv_file_name.split('_')
        inp = []
        inp.append(metadata[0])
        inp.append(exp_name)
        c = 0
        for i in range(1, 10):  # get metadata from file name
            if metadata[i] not in exp_name:  # handles _'s in exp_name
                inp.append(metadata[i])
                c += 1
            if c == 2:  # c == 2 when last metadata retrieved
                break
        return inp, [cluster[x_name], cluster[y_name]]

    def clear_csv_dir(self):
        log.info("Clearing csv directory")
        sleep(3)
        return

    def find_title_click_dropdown(self, title_name: str):
        log.info("Finding dropdown menu")
        sleep(2)
        return [1.0,1.0]

    def select_dropdown_option(self, option_title: str, start_loc: List[float]):
        log.info("Clicking drop down option {}".format(option_title))
        sleep(2)
        return

    def select_target_well(self, target_well: str):
        log.info("Clicking on well {}".format(target_well))
        sleep(2)
        return



