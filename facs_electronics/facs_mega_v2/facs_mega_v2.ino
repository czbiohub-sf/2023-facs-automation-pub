#define CYCLE_TIME 5000
int PWM_ON = 180;
int SLOW_PWM = 100;

// PINOUTS
#define PWM 6
#define DIR 5
#define THERMISTOR_1 A0
#define THERMISTOR_1_D A1
#define THERMISTOR_2 A2
#define THERMISTOR_2_D A3
#define THERMISTOR_3 A4
#define THERMISTOR_3_D A5
#define THERMISTOR_4 A6
#define THERMISTOR_4_D A7
#define THERMISTOR_5 A8
#define THERMISTOR_5_D A9
#define THERMISTOR_6 A10
#define THERMISTOR_6_D A11
//int motor_array[18] = {36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53};
int motor_array[18] = {22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,51,53};
int motor_states[18] = {0};
int num_motors = 18;

//int encoders[18] = {18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35};
int encoders[18] = {16,17,18,19,20,21,23,25,27,29,31,33,35,37,39,41,43,45};
bool detected = false;
int lastRead;
bool firstRead;
long num_tries = 0;

// Housekeeping variables

// Thermistor characteristics
#define TEMPERATURENOMINAL 25
#define THERMISTORNOMINAL 10500
#define NUMSAMPLES 1000
#define BCOEFFICIENT 3950
#define SERIESRESISTOR 10000
#define Vref 3.3
int temp_pins[12] = {54,55,56,57,58,59,60,61,62,63,64,65};
float temp_arr[6] = {0,0,0,0,0,0};
int num_samples = 0;

// Because max_samples is an int, the max samples it can take is 32767. Otherwise, it will go neg.
// We could implement this as a long which will give us 2^31 - 1 (2147483647),
// but that would be allowing averaging over a period > 10 minutes.
// We want to avoid averaging over that long of a period, in the case of rapid changing
// temperature (e.g., when getting to equilibrium), which would cause an avg. temp value not representative of the actual temp.
// So we will average over max 32767 values, which corresponds to roughly ~4mins.
long thresh_samples = 32766;
float T_1;
float T_1_D;
float T_2;
float T_2_D;
float T_3;
float T_3_D;
float T_4;
float T_4_D;
float T_5;
float T_5_D;
float T_6;
float T_6_D;


// Motors
long prevMillis = 0;
boolean newData = false;
const byte numChars = 64;
char receivedChars[numChars];
char argDelimiter = ',';
char cmdDelimiter = '\n';

// Solenoid valve
int solenoid_state = 0;
#define SOL_V 14

// ------------------
// ENCODER FUNCTIONS
// ------------------
bool readEncoders(int motor) {
  int reading = digitalRead(motor);
  bool detection = false;
  if (firstRead == false) {
    lastRead = reading;
    firstRead = true;
  } else {
    if (reading != lastRead) {
      detection = true;
    } else {
      num_tries = num_tries + 1;
      lastRead = reading;
    }
  }
//  Serial.print("Detected: ");
//  Serial.println(detection);
  return detection;
}

// ---------------
// MOTOR FUNCTIONS
// ---------------
void switchDirections() {
  int tempPWM = PWM_ON;
  int prev_state[9] = {0,0,0,0,0,0,0,0,0};

  // Staggers switching motors by turning one row off temporarily.
  // Stores previous states of the motors, in case one or more were intentionally off.

  for (int i = 0; i<9; i++) {
    prev_state[i] = digitalRead(motor_array[i]);
    digitalWrite(motor_array[i], HIGH);
  }
  
  digitalWrite(DIR, !(digitalRead(DIR)));

  for (int i = 0; i<9; i++) {
    digitalWrite(motor_array[i], prev_state[i]);
  }
  
}

void changeSpeed(int new_pwm) {
  // Changes speed of the motor by setting a new PWM.
  analogWrite(PWM, new_pwm);
//  Serial.print("Changed speed to ");
//  Serial.println(new_pwm);
}

void toggleMotor(int motor_num) {
  int currState = digitalRead(motor_array[motor_num]);
  int newState = !(currState);
  digitalWrite(motor_array[motor_num], newState);
  motor_states[motor_num] = currState; // Due to the nEN pin, the motor being powered is the opposite of its state
  Serial.print("[");
  Serial.print(motor_num);
  Serial.print(",");
  Serial.print(!(currState));
  Serial.print(",");
  Serial.print(!(digitalRead(motor_array[motor_num])));
  Serial.println("]");
}

void recvWithEndMarker() {
  // When sending commands to Serial, they must have a newline ending (\n) in order to be successfully parsed.
  static byte ndx = 0;
  char rc;

  while (Serial.available() > 0 && newData == false) {
    rc = Serial.read();

    if (rc != cmdDelimiter) {
      receivedChars[ndx] = rc;
      ndx++;
      if (ndx >= numChars) {
        ndx = numChars - 1;
      }
    }
    else {
      receivedChars[ndx] = '\0'; // terminate the string
      ndx = 0;
      newData = true;
    }
  }
}

// -------------------
// SOLENOID VALVE FCNS
// -------------------

void switchSolenoid() {
  int curr_state = digitalRead(SOL_V);
  digitalWrite(SOL_V, !(curr_state));
  solenoid_state = !(curr_state);
  //Serial.print("Switched solenoid to ");
  //Serial.println(solenoid_state);
}

// ---------------------
// TEMP SENSOR FUNCTIONS
// ---------------------

void clearTemp() {
  // Resets temperature readings.
  memset(temp_arr, 0, sizeof(temp_arr));
  num_samples = 0;
}

float to_steinhart(float resistance) {
  // Converts resistance to temperature reading.
  float steinhart;
  steinhart = resistance / THERMISTORNOMINAL;     // (R/Ro)
  steinhart = log(steinhart);                  // ln(R/Ro)
  steinhart /= BCOEFFICIENT;                   // 1/B * ln(R/Ro)
  steinhart += 1.0 / (TEMPERATURENOMINAL + 273.15); // + (1/To)
  steinhart = 1.0 / steinhart;                 // Invert
  steinhart -= 273.15;                         // convert to C
  return steinhart;
}

float v_to_temp(float deltaV) {
  float x;
  float temp;
  float Rt;
  
  x = (deltaV / Vref) + 0.52;
  Rt = (x * SERIESRESISTOR) / (1 - x);
  temp = to_steinhart(Rt);
  return temp;
}

void collectTemps() {
  // Collects and averages thermistor samples.

  // Local variables needed to collect and average samples.
  uint8_t i;
  float deltaV1;
  float deltaV2;
  float deltaV3;
  float deltaV4;
  float deltaV5;
  float deltaV6;

  if (thresh_samples == num_samples) {
    clearTemp();
  }

  // Collect the samples from 6 thermistors (12 pins)
    T_1 = analogRead(THERMISTOR_1);
    T_1_D = analogRead(THERMISTOR_1_D);
    T_2 = analogRead(THERMISTOR_2);
    T_2_D = analogRead(THERMISTOR_2_D);
    T_3 = analogRead(THERMISTOR_3);
    T_3_D = analogRead(THERMISTOR_3_D);
    T_4 = analogRead(THERMISTOR_4);
    T_4_D = analogRead(THERMISTOR_4_D);
    T_5 = analogRead(THERMISTOR_5);
    T_5_D = analogRead(THERMISTOR_5_D);
    T_6 = analogRead(THERMISTOR_6);
    T_6_D = analogRead(THERMISTOR_6_D);
    delay(10);


  // Convert samples to voltage
  T_1 = T_1 * (3.3 / (pow(2, 10) -1));
  T_1_D = T_1_D * (Vref / (pow(2, 10) - 1));
  T_2 = T_2 * (Vref / (pow(2, 10) - 1));
  T_2_D = T_2_D * (Vref / (pow(2, 10) - 1));
  T_3 = T_3 * (Vref / (pow(2, 10) - 1));
  T_3_D = T_3_D * (Vref / (pow(2, 10) - 1));
  T_4 = T_4 * (Vref / (pow(2, 10) - 1));
  T_4_D = T_4_D * (Vref / (pow(2, 10) - 1));
  T_5 = T_5 * (Vref / (pow(2, 10) - 1));
  T_5_D = T_5_D * (Vref / (pow(2, 10) - 1));
  T_6 = T_6 * (Vref / (pow(2, 10) - 1));
  T_6_D = T_6_D * (Vref / (pow(2, 10) - 1));
  // Take differential voltage and convert to absolute resistance
  deltaV1 = T_1_D - T_1;
  deltaV2 = T_2_D - T_2;
  deltaV3 = T_3_D - T_3;
  deltaV4 = T_4_D - T_4;
  deltaV5 = T_5_D - T_5;
  deltaV6 = T_6_D - T_6;
  float temps[6] = {deltaV1, deltaV2, deltaV3, deltaV4, deltaV5, deltaV6};

  for (int i = 0; i < 6; i++) {
    // Checks that all the temps are within a reasonable range to count it.
    int avg_temp = temp_arr[i] / num_samples;
    if (abs(temps[i] - avg_temp) > 5) {
      return;
    }
  }
  
  for (int i = 0; i < 6; i++) { 
    temps[i] = v_to_temp(temps[i]);
    temp_arr[i] = temp_arr[i] + temps[i];
  }
  
  num_samples++;
}

void setup() {
  // put your setup code here, to run once:

  Serial.begin(9600);

  // Set up PWM signals
  pinMode(PWM, OUTPUT);
  pinMode(DIR, OUTPUT);
  
  // Set up solenoid valve
  pinMode(SOL_V, OUTPUT);
  digitalWrite(SOL_V, solenoid_state);
  
  // Set up motors
  for (int i = 0; i < num_motors; i++) {
      pinMode(motor_array[i], OUTPUT);
      //MAX14870 is pulled down (enabled by default), need to drive it high to disable it
      digitalWrite(motor_array[i], HIGH);
      pinMode(encoders[i], INPUT);
    }
  analogWrite(PWM, PWM_ON);
  digitalWrite(DIR, LOW);
    
  for (int i = 0; i < 12; i++) {
    pinMode(temp_pins[i], INPUT);
  }
  analogReference(EXTERNAL);
  
  Serial.println("Ready");
}

void loop() {
  // put your main code here, to run repeatedly:
  unsigned long currMillis = millis();
  if (currMillis - prevMillis > CYCLE_TIME) {
    prevMillis = currMillis;
    switchDirections();
  }

  collectTemps();
  recvWithEndMarker();
  
  if (newData == true) {
    if (strcmp(receivedChars, "READ_TEMP") == 0) {
      // Arg to ping temperature readings
      for (int i = 0; i < 5; i++) {
        temp_arr[i] = temp_arr[i] / num_samples;
        Serial.print(temp_arr[i]);
        Serial.print(",");
      }
      temp_arr[5] = temp_arr[5] / num_samples;
      Serial.println(temp_arr[5]);
      clearTemp();
      
    } else if (receivedChars[0] == 'M') {
      char * cmdParsed = strtok(receivedChars, &argDelimiter);
      char * argParsed = strtok(NULL, cmdDelimiter);
      int arg = atoi(argParsed);
      if (arg == -1) {
        for (int i = 0; i<num_motors; i++) {
          // The motor state is the opposite of its on-state, due to the nEN pin
            Serial.print(motor_states[i]);
            if (i == (num_motors - 1)) {
              Serial.println("");
            } else {
              Serial.print(",");
            }
          }
      } else {
        Serial.println(motor_states[arg]);
      }
      newData = false;
            
    } else if (receivedChars[0] == 'S') {
      // Arg to toggle motors on/off
      char * cmdParsed = strtok(receivedChars, "S[,]\n");

      // Parses Serial command and adds int to args.
      for ( int i = 0; cmdParsed != NULL; i++) {
//        args[i] = atoi(cmdParsed);
        toggleMotor(atoi(cmdParsed));
        cmdParsed = strtok(NULL, "[,]\n");
      }
    } else if (receivedChars[0] == 'E') {
      // Arg to read encoders, e.g. E,0
        char * cmdParsed = strtok(receivedChars, "E[,]\n");
        char * argParsed = strtok(NULL, cmdDelimiter);
        int idx = atoi(cmdParsed);
     //   Serial.print("Looking at motor: ");
     //   Serial.println(idx);
     //   Serial.println("Slowing motors down...");
        changeSpeed(SLOW_PWM); // NOTE: This will change the speed of all motors.
        digitalWrite(DIR, HIGH); // change them to turn CW
        delay(1000);
    //    Serial.println("Waiting for signal...");
        num_tries = 0;
        while(detected == false) {
          detected = readEncoders(encoders[idx]);
          if (num_tries > 1000000) {
            num_tries = 0;
            break;
          }
        }
        // When it does finally detect something, stop the motors:
        if (detected) {
          Serial.println("Detected");
        } else {
          Serial.println("Not detected");
        }
        detected = false;
        firstRead = false;
        toggleMotor(idx);
        //Serial.println("Restoring motor to original speed");
        //Serial.println(PWM_ON);
        changeSpeed(PWM_ON);
    
   } else if (receivedChars[0] ==  'P') {
      // Arg to change PWM / speed of motors
      char * cmdParsed = strtok(receivedChars, &argDelimiter);
      char * argParsed = strtok(NULL, cmdDelimiter);
      int temp = atoi(argParsed);
      newData = false;
      changeSpeed(temp);
      
    } else if (strcmp(receivedChars, "VALVE") == 0) {
      // Arg to toggle solenoid valve on/off
      switchSolenoid();
      
    } else if (strcmp(receivedChars, "OFF") == 0) {
      // Arg to turn all motors off, including PWM. 
      changeSpeed(0);
      for (int i = 0; i < num_motors; i++) {
          digitalWrite(motor_array[i], LOW);
          motor_states[i] = 0;
       }
      Serial.println("Shut all motors off.");
      
    } else if (strcmp(receivedChars, "ON") == 0) {
      // Arg to turn all motors on
      changeSpeed(PWM_ON);
      for (int i = 0; i < num_motors; i++) {
            digitalWrite(motor_array[i], HIGH);
            motor_states[i] = 1;
      }
    }
    newData = false;
    memset(receivedChars, 0, numChars);
  }
}
