import csv
import os
from pyautogui import scroll, locateOnScreen, moveTo
from subprocess import run, PIPE
from time import sleep
from czfacsautomation.sorting.controller import Controller


"""
This is a script written to scrape ALL sorts after a run is already complete.
"""


# Sequence: Identify all the tubes that have the word 'sort' in them
# Double click it, export the CSV by clicking on 'D'
# Keep track of the ones you have done --> should we assume that all of samples were done?

# Scroll all the way to the bottom
# Using OCR --> find all tubes that say 'sort'
# Then, click + F2 to find the sample name and store it in a list
# Double click to view the profile --> click D gate --> export csv --> close sheet 
#folder = "../../sortdata"
#os.makedirs(folder, exist_ok = True)
def find_sort_type(c) -> str:
    """Determines whether the Sony GUI is in active sorting mode or analyzer mode
    
    :param c: instance of the controller class used in manipulating the Sony GUI
    :type controller: type
    :return: sort name the state of the Sony GUI
    :rtype: str
    """
    
    scroll(-1)
    scroll(-1)
    sleep(0.5)
    loc_active = list(c.find_all_on_screen("SORT_NAME"))
    loc_inactive = list(c.find_all_on_screen("SORT_NAME_INACTIVE"))
    scroll(1)
    scroll(1)
    if len(loc_active) != 0:
        sort_name = "SORT_NAME"
    elif len(loc_inactive) != 0:
        sort_name = "SORT_NAME_INACTIVE"
    else:
        sort_name = None
    return sort_name

def main():
    """Exports all of the data from an experiment in the Sony software
    """
    
    c = Controller(find_btns=False)
    exported = []
    bottom_found = False
    sort_name = None

    Sony_expo = input("Do you need to export from Sony software? (y/n): ")
    if Sony_expo in ['y', 'Y']:

        print("Starting export!")
        sleep(3)
        # First start with scrolling all the way to the bottom, since it's closer
    
        c.scroll_experiment_bar("EXPERIMENT_ICON",step=10)
        exp_name = c.read_experiment_name()
        scroll_bar_exists = c.find_on_screen("SCROLL_BAR", check_none=False)
    
        cwd = os.getcwd()
        folder = f"../../sortdata/{exp_name}"
        os.makedirs(folder, exist_ok=True)
        abs_path = cwd[:cwd.find("\\FACSAutomation")]
    
        print(f"Storing exported data in {folder}")
        # Find all the places with "sort" in its name, return the locations
    
        # Initial routine to figure if it is an active or inactive experiment
        
        while sort_name is None:
            sort_name = find_sort_type(c)
    
        print(sort_name)
        c.return_to_git()
        print("Starting scrape...")
        sleep(5)
        while True:
            locs = list(c.find_all_on_screen(sort_name))
            print(locs)
    
            if len(locs) == 0:
                #no sorts found in the current window.. usually at the start
                print("No sorts found in this window, keep scrolling")
                scroll(-1)
                scroll(-1)
                scroll(-1)
                sleep(0.5)
    
            else:
                print("Locs: ", locs)
                for loc in locs:
                    sample_name = c.find_sort_data(loc)
                    if sample_name not in exported:
                        print(f"Found new sample to export: {sample_name}")
                        exported.append(sample_name)
                        sample_folder = f"{folder}/{sample_name}"
                        os.makedirs(sample_folder)
                        c.export_sort_data(sample_name, sample_folder)
                        # Screenshot the last one sorted
                        print("finished exporting sort data")
                        c.screenshot_last_sort(folder, loc) # Keeps the last exported sort in memory for scrolling faster
                        c.export_csv_and_close_sheet(loc=f"{abs_path}\\sortdata\\{exp_name}\\{sample_name}", scraper=True)
                        print("Getting gate vertices")
                        get_cmd = run(['GateVertexTool', 'get', c.file_name[0],
                                       c.file_name[1], c.file_name[2], 
                                       c.file_name[3]], stdout=PIPE)
                        if get_cmd.returncode == 0: #It was successful
                            get_output = get_cmd.stdout.splitlines()
                            last_gate = get_output[3].split()  # last gate in row 3
                            filename = f"{sample_folder}/{sample_name}_gate.csv"
                            with open(filename, 'w') as csvfile:
                                csvwriter = csv.writer(csvfile)
                                csvwriter.writerow(last_gate)
                            print("Completed export.")
                        else:
                            print("Could not retrieve gate vertices.")
                        moveTo(loc)
    
            
            bottom_found = c.find_on_screen("SCROLL_BAR_BOTTOM", check_none=False)
            if bottom_found is not None and scroll_bar_exists is not None:
                break
            elif scroll_bar_exists is None:
                # there was only ~1 sample to export, just break
                break
            # Keep scrolling, there must be more samples ( i think each window will have 3 samples ? )
            # While you cannot find the last one sorted
            while True and len(locs) != 0:
                loc = locateOnScreen(f"{folder}/last_sort.png", confidence = 0.98)
                bottom_found = c.find_on_screen("SCROLL_BAR_BOTTOM",check_none=False)
                scroll(-1)
                sleep(1)
                if loc is None or bottom_found is not None:
                    scroll(1)
                    break
        # Remove the 'last_sort.png' file
        os.remove(f"{folder}/last_sort.png")
        print(f"Exported the following samples: {exported}")
        print("Export complete.")
    c.return_to_git()




if __name__ == "__main__": 
    try:
        main()
    except Exception as e:
        print("=================================")
        print("=================================")
        print("There was a problem. Please fix")
        print(e)