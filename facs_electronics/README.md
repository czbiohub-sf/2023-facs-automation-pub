# FACSAutomation
Python libraries for automating cell sorting with the Sony SH800S GUI.

# Serial Commands
All commands should be sent via Serial with a newline ending, `\n`, e.g. send `VALVE\n`.
Upon initialization, all 18 motors are initialized but turned off, and the valve is switched open.
| Command | Description |
|--|--|
| `VALVE` | Toggles solenoid valve on/off. Solenoid is normally closed but initialized open. |
|`READ_TEMP` | Upon calling, will average collected temperature readings from 6 sensors and return in a string 0,0,0,0,0,0 |
|`M,X` | Reads motor status, where X is the motor of interest (zero-indexed). Let X = -1 to return all motor statuses in the form 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.|
|`S,[X]` | Switches state of motors, where X can be a variable list of motor nums (zero-indexed); e.g., `S,[0,1,2,17]` to toggle motor # 0, 1, 2, and 17 or `S,[0]` to toggle just the first motor. Will return `[motor_num, old state, new state]`, e.g. `[5, 1, 0]` if turning off the 5th (0-indexed) motor.|
|`E,X` | Stops motors based on the encoder reading. The motor must be turned on using `S,[X]` before using the encoder. When the encoder successfully picks up a signal, it will return:<br>`Detected`<br> `[motor_num,1,0]`<br>If it is unsuccessful, it will return: <br>`Not detected`<br>`[motor_num,1,0]`|
|`P,X`| Changes PWM of motors to X, ranging from 0-255.|
| `ON`| Turns all 18 motors on and sets PWM to 150.
| `OFF`| Turns all motors off AND sets PWM to 0 (think low-power OFF). To turn back on, either use `P,X` to set PWM and then toggle motors with `S,[X]` to turn on motors; or, `ON` to set PWM to 150 and enable all 18 motors. |