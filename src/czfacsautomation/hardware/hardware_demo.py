import sys
from time import sleep
from czfacsautomation.hardware.hardware_controller import HardwareController


def main(location = sys.argv[1]) -> bool:
    """
    Demo of the hardware rotating tubes and shuttling to and from Sony SH800
    
    :param location: the system location for each physical instrument
    :type location: str
    :raises Exception: logs if the hardware config file not found or hardware does not connect
    :return: A bool as to whether a the code ran successfully through all steps.
    :rtype: bool
    """
    
    # Initialize and connect to hardware controller
    try:
        hc = HardwareController(location)
        hc.connect_hardware('prod')
        proceed = True
    except Exception as e:
        print("Could not initialize and connect hardware controller")
        proceed = False
    
    if proceed:
        # Toggle the solenoid vavle to cool the tube housing when the motors are running
        hc.ac.toggle_solenoid_valve()
        print('Solenoid valve actuated to cool housing, a minimum of 10 min is needed to reach equilibrium temperature.')
    
        for i in range(18):
            hc.ac.toggle_motor(i)
            sleep(2)
            hc.ac.toggle_motor(i, False)
            hc.start_sort(i)
            hc.finish_sort(i)
        hc.run_complete()

    return proceed
        

if __name__ == "__main__":
    proceed = main(sys.argv[1])

    if not proceed:
        print("Exited with error(s)")
    else:
        print("Exited with no errors")