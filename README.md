# FACSAutomation

## Introduction
This repository contains the Python application and custom **czfacsautomation** package that have been designed for automating the cell sorting on the Sony SH800S, by the CZ Biohub Bioengineering team. All utilities support Python 3.7. Note that newer versions of Python are not compatible.

Maintenance of this repo is the responsibility of Diane Wiener. Please direct any communication to Diane Wiener. 

This source describes Open Hardware, which is licensed under the CERN-OHL-W v2. 

Electronics hardware is described in the facs_electronics folder.

CAD designs are provided in Onshape: https://cad.onshape.com/documents/c1a3ab256e8df7a71b82db8c/w/ab65c37920d47d4a2484a277/e/421207c6e308bccf3dd4e5b1?configuration=default&renderMode=0&uiState=640b930bf24bcf207edf60a6

Software is licensed under BSD 3-Clause.

Copyright Chan Zuckerberg Biohub 2023.

## Contents

### Classes
/hardware/
* __HardwareController__ - Interfaces with hardware peripherals
* __ZaberController__ - Communicates with the zaber stages and gripper
* __ArduinoController__ - Communicates with the arduino via serial

/sorting/
* __Controller__ - Creates wrapper classes for auto click methods used for interfacing with the Sony SH800S GUI
* __Sort__ - Runs a single sort on the Sony SH800S GUI
* __Gating__ - Runs the GateVertexTool to get and set gate on the Sony SH800S GUI
* __CreateGate__ - Creates a custom gate using the cell population data

/integration/
* __FACSAutomation__ - Main class to call, starts process, and implements pause/stop

/slack/
* __SlackFacs__ - Communicates with Slack App to notify users of current run status.

### Config Files
/config/
* __hardware_config.json__ - Holds the hardware configuration parameters for the zaber stages and arduino
* __gui_config.json__ - Holds the config file of all screenshots and parameters needed to run sorting
* __Slack_config.json__ - Holds the configuration parameters for the various messages to post

### Vendor Folder
The GateVertexTool `GateVertexTool.exe` is available from Sony Biotechnology.
Requests to access the GateVertexTool may be made to SONY Biotechnology via the following 
URL: https://go.sonybiotechnology.com/gate-vertex.html.
Store the file in the `vendor/GateVertexTool` folder.

## Installation and Use
### Installing Module
1. On Windows OS: Add GateVertexTool folder to "Path" environment variable (read release notes for more details)
2. Create and/or activate a virtual environment in a convenient location with Python3
3. Install and add pytesseract to path
4. Download / clone this repository
5. Navigate to the base of the repository
6. Install setuptools `__pip install setuptools__`
7. Install module `__pip install -e .__`
8. Create the folder for the exported gating data in the location specified in the "GATE_CSV_DIR" path in the `gui_config.json` 

### Updating Module from Repository
1. Pull changes from remote repository
2. Activate virtual environment with previous install
3. Navigate to the module directory
4. Update module `__pip install -e . --upgrade__`

### Using Module
1. cd to the `src` directory
2. `python -m czfacsautomation "<hardware_config location>" "-facs" ""`

#### Module Routines:
1. Chill Tube Housing:
   
   `python -m czfacsautomation "<hardware_config location>" "-chill" ""`

2. Run FACS Automation:
   
   `python -m czfacsautomation "<hardware_config location>" "-facs" ""`

3. Data Scraper:
   
   `python -m czfacsautomation "<hardware_config location>" "-scrape" ""`

4. Hardware Demo:
   
   `python -m czfacsautomation "<hardware_config location>" "-demo" ""`

5. Calibration:
   
   a. Calibration Update Scan:
      
   `python -m czfacsautomation "<hardware_config location>" "-calibrate" "-s"`
   
   b. Tube Calibration Check:
      
   `python -m czfacsautomation "<hardware_config location>" "-calibrate" "-t"`
   
   c. Full Calibration Routine (Scanning and with Tubes):
      
   `python -m czfacsautomation "<hardware_config location>" "-calibrate" "-f"`
