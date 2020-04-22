# Robotic Arm Controller

Arduino firmware to control a robotic arm such as [EEZYbotARM](https://www.thingiverse.com/thing:1015238). Tested with EEZYbotARM in Mega2560.

An example client in Python to use as a starting point for higher level behavior.

Changelog:

- Initial version. Minimal servo control.

## Dependencies

- [arduino-cli](https://github.com/arduino/arduino-cli)
- [Servoeasing](https://github.com/ArminJo/ServoEasing)

## Usage

### Robot setup

Default Arduino Mega Pins for EEZYbotARM:

|Servo          | Pin(*) | Idle | Range                     |
|---------------|--------|------|---------------------------|
|Servo A (Base)-| 3      | ??   |                           |
|Servo B (Arm1)-| 4      | 90   |                           |
|Servo C (Arm2)-| 5      | 130  |                           |
|Servo D (Tool)-| 6      | 120  | ~86 (Closed) / 180 (Open) |

Note: remember to connect ground from arduino to external power supply.

### Firmware building and uploading (arduino-cli)

List boards.

```
arduino-cli board list
Port         Type              Board Name                        FQBN             Core       
/dev/ttyACM1 Serial Port (USB) Arduino/Genuino Mega or Mega 2560 arduino:avr:mega arduino:avr
```

Compile and upload.

```
arduino-cli compile --fqbn arduino:avr:mega .
arduino-cli upload -p /dev/ttyACM1 --fqbn arduino:avr:mega .
```

### Bench test script

A jupyter notebook is provided to test communication with the robot.

```
cd python
jupyter notebook
```

### Communication Protocol

A simple serial protocol is used. Commands have the following structure:

```
"CMD!"<length><payload><crc16>'\n'
```

where:
- length is a byte indicating the length of payload.
- payload is a sequence of length bytes.
- crc16 is the calculated CRC16 of the payload.



Commands and telemetry are defined in [cmd_def.h](cmd_def.h) and [tmy_def.h](tmy_def.h)

#### Commands

All arguments are one byte.

| Command                | Purpose                 | Arguments                                                    |
| ---------------------- | ----------------------- | ------------------------------------------------------------ |
| REQUEST_TMY            | Request Telemetry       | None                                                         |
| LED_ON                 | Turn on test led        | None                                                         |
| LED_OFF                | Turn off test led       | None                                                         |
| ECHO                   | Echo                    | Array of bytes (max size=Command Buffer Size)                |
| UPDATE_SERVO_POSITIONS | Move one or more servos | The four servo angles in degrees (0-180) and a mask where 0x1 is the first servo, 0x2 the second, etc. |

#### Telemetry

All parameters are one byte.

| Offset | Parameter                        |
| ------ | -------------------------------- |
| 0      | TMY_PARAM_ACCEPTED_PACKETS       |
| 1      | TMY_PARAM_REJECTED_PACKETS       |
| 2      | TMY_PARAM_LAST_OPCODE            |
| 3      | TMY_PARAM_LAST_ERROR             |
| 4      | TMY_PARAM_MODE                   |
| 5      | TMY_PARAM_SERVO1_CURR_POSITION   |
| 6      | TMY_PARAM_SERVO1_TARGET_POSITION |
| 7      | TMY_PARAM_SERVO2_CURR_POSITION   |
| 8      | TMY_PARAM_SERVO2_TARGET_POSITION |
| 9      | TMY_PARAM_SERVO3_CURR_POSITION   |
| 10     | TMY_PARAM_SERVO3_TARGET_POSITION |
| 11     | TMY_PARAM_SERVO4_CURR_POSITION   |
| 12     | TMY_PARAM_SERVO4_TARGET_POSITION |