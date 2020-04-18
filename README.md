# Robotic Arm Controller

Arduino firmware to control a robotic arm such as [EEZYbotARM](https://www.thingiverse.com/thing:1015238).
Tested in Mega2560.

## Dependencies

- [arduino-cli](https://github.com/arduino/arduino-cli)
- [Servoeasing](https://github.com/ArminJo/ServoEasing)

## Usage

### Robot setup

Arduino Pins for EEZYbotARM:

|Servo          | Arduino Pin(*)  |
|---------------|-----------------|
|Servo A (Base)-| 3               |
|Servo B (Arm1)-| 4               |
|Servo C (Arm2)-| 5               |
|Servo D (Tool)-| 6               |

(*) Mega

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

### Commication Protocol

A simple serial protocol is used. Commands have the following structure:

"CMD!"<length><payload><crc16>'\n'

where:
- length is a byte indicating the length of payload.
- payload is a sequence of length bytes.
- crc16 is the calculated CRC16 of the payload.