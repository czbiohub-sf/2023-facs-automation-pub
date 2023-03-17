import logging
from subprocess import run, PIPE
import sys
from time import sleep
from typing import List, Tuple
from czfacsautomation.sorting import CreateGate


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s',"%H:%M:%S")
handler.setFormatter(formatter)
log.addHandler(handler)


class Gating():
    """Calls the GateVertexTool and gets and sets the gate
    """

    def __init__(self, gate_variables: List[str], dataset: Tuple[List[float], List[float]]):
        """Initializes the instance variables

        :param gate_variables: Metadata of the experiment
                [<user>, <exp_name>, <group_name>, <sample_name>]
        :type gate_variables: List[str]
        :param dataset: Scatter plot data
                    [<x coordinates>, <y coordinates>] 
        :type dataset: Tuple[List[float], List[float]]
        """
        
        self.gate_variables = gate_variables
        self.dataset = dataset
        
    def gate(self):
        """Runs the gating process of retrieving the gate vertices, making the new
        gate, and passing the new gate vertices back to the Sony database using
        the GateVertexTool
        """
        
        log.info('Gating: Getting Gate')
        gate_id = self._get()
        
        log.info('Gating: Creating Custom Gate')
        shape, coord = self._manipulate_gate()
        
        log.info('Gating: Setting Gate')
        self._set(gate_id, shape, coord)
            
    def _get(self) -> str:
        """Runs get and returns the gate id for the 4th gate

        
        :return: The id of the 4th gate needed for the set command
        :rtype: str
        """
        
        log.info(f"Gate variables: {self.gate_variables}")
        get_cmd = run(['vendor/GateVertexTool', 'get', self.gate_variables[0], 
                    self.gate_variables[1], self.gate_variables[2], 
                    self.gate_variables[3]], stdout=PIPE)
        if self._is_successful(get_cmd.returncode):
            get_output = get_cmd.stdout.splitlines()
            last_gate = get_output[3].split()  # last gate in row 3
            return last_gate[1].decode('utf-8')
        else:
            self._get(self.gate_variables)

    def _set(self, gate_id: str, shape: str, coord: str):
        """Sets the gate on the SONY Software

        :param gate_id: The id of the gate that is being set
        :type gate_id: str
        :param shape: The shape of the gate (Polygon)
        :type shape: str
        :param coord: The coordinates in a str format
                'x1, y1, x2, y2, ...'
        :type coord: str
        """
        
        log.info(f"Gate ID variables: {gate_id}")
        set_cmd = run(['GateVertexTool','set', gate_id, shape, coord])
        if not self._is_successful(set_cmd.returncode):
            self._set(gate_id, shape, coord)

    def _manipulate_gate(self) -> Tuple[str, str]:
        """Create a custom gate for the dataset

        :return: The shape of the gate and the gate coordinates
        :rtype: Tuple[str, str]
        """
        
        c = CreateGate(self.dataset[0], self.dataset[1])
        cp = c.create_gate()
        return 'Polygon', c.update_gate_format()


    def _is_successful(self, returncode: int) -> bool:
        """Prompt user to retry if the returncode is not success

        The expected failures should mainly be during debugging and will
        require manual fixes. The method retries the get/set tool 
        if the user inputs enter.

        :param returncode: The code returned by the get/set tools
        :type returncode: int
        :return: True: Sucess, False: Failed of using the GateVertexTool
        :rtype: bool
        """

        if returncode == 0:
            return True
        else:
            log.critical('Failed using GateVertexTool with error {}'.format(returncode))
            log.critical('Will retry again in 5s')
            log.critical('Enter <shift>+p to pause or <shift>+s to stop')
            sleep(5)
            return False