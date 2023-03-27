import getopt
import json
import os
import sys
from pkg_resources import Requirement, resource_filename
from time import sleep
from czfacsautomation.hardware.arduino_controller import ArduinoController
from czfacsautomation.hardware.hardware_controller import HardwareController
from czfacsautomation.integration.facs_automation import FACSAutomation
from czfacsautomation.sorting.sorting_automation import Sort, MockSort


def calib_position(hc, rail) -> int:
    """Updates the Zaber stage positions at the tube housing
    
    :param hc: Instance of the hardware controller class
    :type hc: type
    :param rail: The dictionary of relevant data for each sample
    :type rail: str
    :raises: Exception when the input from the user to change the postion is not valid 
    :return: The updated position information for the Zaber stages
    :rtype: int
    """
    if rail == 'lower_rail':
        tube = 'tube0'
    else:
        tube = 'tube9'

    x = hc.zaber_config[tube]['x']
    y = hc.zaber_config[rail]['y']['in']
    z = hc.zaber_config['inner_spacing']['spacing']

    while True:
        # X CALIBRATION
        resp = input("Enter how much you want to change the x position by (in mm). If none, enter 0: ")
        try:
            resp = float(resp)
            if not resp:
                # Response is 0, break out
                break
            else:
                x += resp
                if x >= 235.5 and rail == 'lower_rail':
                    print(f"New position exceeds the maximum of 235.5 mm. Returning to previous position. Try again with a smaller step size.")
                    x -= resp
                    break
                if x >= 260.5 and rail == 'upper_rail':
                    print(f"New position exceeds the maximum of 260.5 mm. Returning to previous position. Try again with a smaller step size.")
                    break
                hc.zaber_config[tube]['x'] = x
                hc.zc.prep_tube_housing_pickup(int(tube[-1]))
                hc.zc._move_arm('y', y)
                hc.zc._grab_tube()
        except Exception as e:
            print("Invalid response. Please try again.")

    
    print("You will now be calibrating the y position.")

    while True:
        # Y CALIBRATION
        resp = input("Enter how much you want to change the y position by (in mm). If none, enter 0: ")
        try:
            resp = float(resp)
            if not resp:
                # Response is 0, break out
                break
            else:
                y += resp
                if y >= 41.5 and rail == 'lower_rail':
                    print(f"New position exceeds the maximum of 41.5 mm. Returning to previous position. Try again with a smaller step size.")
                    y -= resp
                    break
                if y >= 90 and rail == 'upper_rail':
                    print(f"New position exceeds the maximum of 90 mm. Returning to previous position. Try again with a smaller step size.")
                    break
                hc.zaber_config[rail]['y']['in'] = y
                hc.zc.prep_tube_housing_pickup(int(tube[-1]))
                hc.zc._move_arm('y', y)
                hc.zc._grab_tube()
        except Exception as e:
            print("Invalid response. Please try again.")


    print("Now that the first position is calibrated you will be calibrating the spacing.")
    while True:
        # SPACING CALIBRATION
        # Moves arm into place
        if rail == "lower_rail":
            hc.zc.prep_tube_housing_pickup(8)
        else:
            hc.zc.prep_tube_housing_pickup(17)
        hc.zc._move_arm('y', hc.zaber_config[rail]['y']['in'])
        hc.zc._grab_tube()

        resp = input("Enter how much you want to change the spacing by (in mm). If none, enter 0: ")
        try:
            resp = float(resp)
            if not resp:
                break
            else:
                z += resp
                hc.zaber_config['inner_spacing']['spacing'] = z
        except Exception as e:
            print("Invalid response. Please try again.")
        

    return x,y,z

def main(location = sys.argv[1], calibration = sys.argv[2:]) -> bool:
    """Runs the calibration routine, setting up which of the series of calibrations to complete.
    
    
    :param calibration: the string specifying which series of calibrations to perform
    :type calibration: str
    :raises GetoptError: when the option is not recognize from the accepted list
    :raises: any eception that cannot be handled with the hardware controller
    :return: state of the software run, whether it completed successfully or encountered an error
    :rtype: bool
    """
    fullTest = False
    doScan = False
    withTubes = False

    if calibration == '-h':
        print("calibration.py -s -t -f")
        sys.exit()
    elif calibration in ("-s", "--scan"):
        doScan = True
    elif calibration in ("-t", "--tube"):
        withTubes = True
    elif calibration in ("-f", "--fullTest"):
        doScan = True
        withTubes = True

    proceed = True

    if proceed:
        # Initialize hardware controller
        try:
            hc = HardwareController(location)
        except Exception as e:
            print("Could not initialize hardware controller")
            proceed = False
    
    if proceed:
        # Connect to hardware devices
        try:
            # Change this to prod if testing on TC computer
            hc.connect_hardware('prod')
        except Exception as e:
            print("Could not load hardware devices")
            proceed = False

    if proceed and doScan:
        # Move into initial position
        try:
            input("Press enter after making sure there are no tubes in the housing or other obstacles!")
            print("Starting at first tube position with default configurations")
            rail = 'lower_rail' 
            x = hc.zaber_config['tube0']['x']
            y = hc.zaber_config[rail]['y']['in']

            hc.zc.prep_tube_housing_pickup(0)
            hc.zc._move_arm('y', y)
            hc.zc._grab_tube()

            z = hc.zaber_config['inner_spacing']['spacing']
            print(f"Config x position is: {x}")
            print(f"Config y position is: {y}")
            print(f"Config spacing is: {z}")


        except Exception as e:
            print("Could not move to first tube position")
            proceed = False

        
    if proceed and doScan:
        try:
            print("You will now be calibrating the x, y, and spacing positions for the lower rail.")

            x_lower,y_lower,z_update = calib_position(hc,rail)
            
            print("-----------------------------------------------------")
            print(f"Lower rail: Calibrated config x position is: {x_lower} mm")
            print(f"Lower rail: Calibrated config y position is: {y_lower} mm")  
            print(f"Lower rail: Calibrated config spacing is: {z_update} mm")
            print("-----------------------------------------------------")

        except Exception as e:
            print("Ran into error while calibrating.")
            print(e)
            proceed = False

    if proceed and doScan:
        try:
            print("Moving on to calibrating the upper rail.")
            rail = 'upper_rail' 
            x = hc.zaber_config['tube9']['x']
            y = hc.zaber_config[rail]['y']['in']

            hc.zc.prep_tube_housing_pickup(9)
            hc.zc._move_arm('y', y)
            hc.zc._grab_tube()

            z = hc.zaber_config['inner_spacing']['spacing']

            print(f"Config x position is: {x}")
            print(f"Config y position is: {y}")
            print(f"Config spacing is: {z}")

        except Exception as e:
            print("Ran into error while calibrating.")
            print(e)
            proceed = False
    
    if proceed and doScan:
        try:
            print("You will now be calibrating the x, y, and spacing positions for the upper rail.")
            x_upper,y_upper,z_update = calib_position(hc,rail)
            print("-----------------------------------------------------")
            print(f"Upper rail: Calibrated config x position is: {x_upper} mm")
            print(f"Upper rail: Calibrated config y position is: {y_upper} mm")  
            print (f"Upper rail: Calibrated config spacing is: {z_update} mm")
            print("-----------------------------------------------------")

        except Exception as e:
            print("Ran into error while calibrating.")
            print(e)
            proceed = False

    if proceed and doScan:
        # Now that calibration is complete -- Scan 18 tubes
        print("Configs are fully calibrated. Starting tube housing scan.")   
        try:
            for i in range(18):
                hc.zc._move_arm('y', hc.zaber_config['Sony_clearance'])
                hc.zc.prep_tube_housing_pickup(i)
                rail = 'upper_rail' if i >= 9 else 'lower_rail'
                hc.zc._move_arm('y', hc.zaber_config[rail]['y']['in'])
                hc.zc._grab_tube()
                input("Press enter to proceed to the next tube.")

        except Exception as e:
            print("Ran into error during scan.")
            print(e)
            proceed = False

    if proceed and doScan:
        # Now update config file with new calibration
        print("Updating configuration file.")
        try:
            filelocation = '{}{}\{}'.format('config\\hardware_config\\', location, 'hardware_config.json')
            hw_config_file = resource_filename(Requirement.parse("czfacsautomation"), filelocation)
            with open(hw_config_file, 'r') as hw:
                hardware = json.load(hw)
                hardware['zaber_config']['tube0']['x'] = x_lower
                hardware['zaber_config']['lower_rail']['y']['in'] = y_lower
                hardware['zaber_config']['inner_spacing']['spacing'] = z_update
                hardware['zaber_config']['tube9']['x'] = x_upper
                hardware['zaber_config']['upper_rail']['y']['in'] = y_upper
                hw.close()
            with open(hw_config_file, 'w') as hw:
                hardware_update = json.dump(hardware, hw, indent = 4, separators= (',',': '))
                hw.close()

        except Exception as e:
            print("Ran into error updating configuration file.")
            print(e)
            proceed = False

    if proceed and withTubes:
        input("Press enter after filling tube housing with tubes for attempted pickup/dropoff.")
        print("Attemping pick up and drop off of all tubes.")
        try:
            hc.zc._move_arm('y', hc.zaber_config['Sony_clearance'])
            hc.zc._move_z_tube_housing(0, True)
            hc.zc._move_arm('g', hc.zaber_config['claw']['tube_clearance'])
            for i in range(18):
                hc.ac.toggle_motor(i)
                sleep(5)
                hc.ac.toggle_motor(i, False)
                hc.start_sort(i)
                hc.finish_sort(i)
            print("Tube pickup/dropoff completed. Disconnecting hardware.")
        except Exception as e:
            print("Ran into an error while attempting tube pick up and drop off.")
            proceed = False
    
    hc.run_complete()

    return proceed

if __name__ == "__main__":
    proceed = main(location = sys.argv[1], calibration = sys.argv[2:])

    if not proceed:
        print("Exited with error(s)")
    else:
        print("Exited with no errors")