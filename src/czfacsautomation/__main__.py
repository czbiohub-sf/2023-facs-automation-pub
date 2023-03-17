import os, sys, subprocess
from time import sleep

import czfacsautomation
from czfacsautomation.integration.facs_automation import FACSAutomation
from czfacsautomation.hardware.chill_house import main as ChillHouse
from czfacsautomation.hardware.hardware_demo import main as HardwareDemo
from czfacsautomation.hardware.calibration import main as Calibrate
from czfacsautomation.integration.sort_scraper import main as SonyScrape
from czfacsautomation.integration.plot_exported_data import main as SonyPlot

def _chill_house(location) -> int:
    """Turns on the air supply for cooling.
    
    :param location: the system location for each physical instrument 
    :type location: str
    :raises: Any exception that cannot be handled internally with the chill house software
    :return: state of the software run, whether it completed successfully or encountered an error
    :rtype: int
    """
    proceed = True
    
    if proceed:
        try:
            ChillHouse(location)
        except Exception as e:
            print("Error turning on solenoid valve.")
            print(e)
            proceed = False
    
    if proceed:
        print("Exiting without errors...")
        
    if not proceed:
        print("Exiting with errors...")
        
    return int(proceed)

def _scrape() -> int:
    """Collects all of the data from the Sony sorter, plots, and saves it
    
    :raises: Any exception that cannot be handled internally with the data scraper software
    :return: state of the software run, whether it completed successfully or encountered an error
    :rtype: int
    """
    
    proceed = True
    
    if proceed:
        try:
            scraper = SonyScrape()
        except Exception as e:
            print("Error with extracting data.")
            print(e)
            proceed = False

    if proceed:
        try:
            plot = SonyPlot()
        except Exception as e:
            print("Error with plotting data.")
            print(e)
            proceed = False
    
    if proceed:
        print("Exiting without errors...")
        
    if not proceed:
        print("Exiting with errors...")
        
    return int(proceed)            

def _run_facs(location) -> int:
    """Calls the facs automation class to run the automation.
    
    :param location: the system location for each physical instrument 
    :type location: str
    :raises: Any exception that cannot be handled internally with the facs automation software
    :return: state of the software run, whether it completed successfully or encountered an error
    :rtype: int
    """
    
    proceed = True
    facs = FACSAutomation(location)
    
    doSetup = False
    setup = input("Do you need to profile a control (wild-type) sample in order to setup or adjust the gates (y/n): ")
    if setup in ['y', 'Y']:
        doSetup = True

    if proceed:
        try:
            facs._connect_hardware()
            facs.start_solenoid()
        except Exception as e:
            print("Could not connect to hardware and toggle solenoid.")
            print(e)
            proceed = False
    
    if proceed:
        try:
            facs._initialize_classes()
        except Exception as e:
            print("Could not initialize classes.")
            print(e)
            proceed = False     
    
    if proceed:
        try:
            facs._start_threads()
        except Exception as e:
            print("Could not start listener threads.")
            print(e)
            proceed = False
            
    if proceed:
        try:
            exp_name = facs._user_setup()
        except Exception as e:
            print("Error with user inputs.")
            print(e)
            proceed = False
    
    if proceed:
        print("STARTING AUTOMATION! Do not touch the computer moving forward.", end="\n\n")
        sleep(3)
        try:
            if doSetup:
                facs.experiment_setup()    
            else:
                facs.experiment_continuation()
            facs.run_sequence(exp_name, facs.data_dict)
        except Exception as e:
            print("Ran into an exception during automation:", e)
            proceed = False
        
    facs.cleanup()
            
    if proceed:
        print("Exiting without errors...")
        
    if not proceed:
        print("Exiting with errors...")
        
    return int(proceed)
    
def _hardware_demo(location) -> int:
    """Runs the hardware, rotating tubes and shuttling to and from Sony SH800.
    
    :param location: the system location for each physical instrument 
    :type location: str
    :raises: Any exception that cannot be handled internally with the hardware software
    :return: state of the software run, whether it completed successfully or encountered an error
    :rtype: int
    """
    proceed = True
    
    if proceed:
        try:
            HardwareDemo(location)
        except Exception as e:
            print("Error turning on solenoid valve.")
            print(e)
            proceed = False
    
    if proceed:
        print("Exiting without errors...")
        
    if not proceed:
        print("Exiting with errors...")
        
    return int(proceed)

def _hardware_calibration(location, calib) -> int:
    """Runs the hardware calibration routine.
    
    :param location: the system location for each physical instrument 
    :type location: str
    :param calib: the calibration routine to perform
    :type calib: str    
    :raises: Any exception that cannot be handled internally with the hardware software
    :return: state of the software run, whether it completed successfully or encountered an error
    :rtype: int
    """
    proceed = True
    
    if proceed:
        try:
            Calibrate(location, calib)
        except Exception as e:
            print("Error turning on solenoid valve.")
            print(e)
            proceed = False
    
    if proceed:
        print("Exiting without errors...")
        
    if not proceed:
        print("Exiting with errors...")
        
    return int(proceed)

    
def main(location = sys.argv[1], program = sys.argv[2], calib = sys.argv[3]):
    """Run one of three rourtines, the automation, the cooling, or data scraping.
    
    :param location: the system location for each physical instrument 
    :type location: str
    :param program: the specific routine to call
    :type program: str
    """
    
    print("=================================")
    print("Welcome to the FACS Automation Software.")
    print("=================================")
    
    if program == '-chill':
        exit_code = _chill_house(location)
    elif program == '-facs':
        exit_code = _run_facs(location)
    elif program == '-scrape':
        exit_code = _scrape()
    elif program == '-demo':
        exit_code = _hardware_demo(location)
    elif program == '-calibrate':
        exit_code = _hardware_calibration(location, calib)
        
    sys.exit(exit_code)
            
if __name__ == "__main__":
    try:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    except Exception as e:
        print("=================================")
        print("=================================")
        print("There was a problem. Please fix")
        print(e)