import serial, time

DEFAULT_SERIAL_PORT = '/dev/ttyUSB0'
DEFAULT_BAUDRATE = 115200

def build_packet(payload):
    pkt = bytearray([ ord('P'), ord('K'), ord('T'), ord('!')] )
    pkt.append(len(payload))
    for x in payload:
        pkt.append(x)
    crc = crc16(payload)
    pkt.append( (crc>>8) & 0xFF )
    pkt.append( crc&0xFF) 
    pkt.append(ord('\n'))
    return pkt

def crc16(buf):    
    crc = 0xFFFF
    for bi in buf:
        x = crc >> 8 ^ bi
        x ^= x>>4
        crc = ((crc << 8)&0xFFFF) ^ ((x << 12)&0xFFFF) ^ ((x <<5)&0xFFFF) ^ (x&0xFFFF)
    return crc

class RobotArmConn:
    
    # Command & Telemetry Definition
    
    CMD_REQUEST_TMY = 0
    CMD_LED_ON = 1
    CMD_LED_OFF = 2
    CMD_ECHO = 3
    CMD_UPDATE_SERVO_POSITION = 4
    
        
    TMY_PARAM_ACCEPTED_PACKETS=0
    TMY_PARAM_REJECTED_PACKETS=1
    TMY_PARAM_LAST_OPCODE=2
    TMY_PARAM_LAST_ERROR=3
    TMY_PARAM_MODE=4
    TMY_PARAM_SERVO1_CURR_POSITION=5
    TMY_PARAM_SERVO1_TARGET_POSITION=6
    TMY_PARAM_SERVO2_CURR_POSITION=7
    TMY_PARAM_SERVO2_TARGET_POSITION=8
    TMY_PARAM_SERVO3_CURR_POSITION=9
    TMY_PARAM_SERVO3_TARGET_POSITION=10
    TMY_PARAM_SERVO4_CURR_POSITION=11
    TMY_PARAM_SERVO4_TARGET_POSITION=12
    
    def __init__(self, port=DEFAULT_SERIAL_PORT, baudrate=DEFAULT_BAUDRATE):
        self.port = port
        self.baudrate=baudrate
        self.robot_conn = None
                
    def connect(self):
        self.robot_conn = serial.Serial( self.port, self.baudrate,timeout=1)
        
    def disconnect(self):
        self.robot_conn.close()
        
    # Basic Protocol Leds and TMY
    def request_tmy(self, retries=25, interval_between_retries=0.5):
        tmy = None
        tmy_valid = False
        attempts = retries
        pkt = build_packet([RobotArmConn.CMD_REQUEST_TMY])
        while attempts > 0 and not tmy_valid:
            self.robot_conn.write(pkt)
            tmy = self.robot_conn.read(14)
            expected_tmy_len = (len(tmydef['params'])+1)
            tmy_valid = (len(tmy) == expected_tmy_len )
            if not tmy_valid and attempts > 0:
                print("Invalid TMY. Expected", expected_tmy_len ,"Received: ", len(tmy) )
                time.sleep(interval_between_retries)
                attempts-=1 
        if not tmy_valid:
            raise ValueError("Invalid Telemetry")
        return tmy
        
    def led_on(self):
        pkt = build_packet([RobotArmConn.CMD_LED_ON])
        self.robot_conn.write(pkt)
        
    def led_off(self):
        pkt = build_packet([RobotArmConn.CMD_LED_OFF])
        self.robot_conn.write(pkt)
        
    def echo(self, payload):
        tmp = [RobotArmConn.CMD_ECHO]
        for x in payload:
            tmp.append(x)
        pkt = build_packet(tmp)
        self.robot_conn.write(pkt)    
        return self.robot_conn.readline()
        
    # Robot Arm Commands        
    SERVO_A = 0x01
    SERVO_B = 0x02
    SERVO_C = 0x04
    SERVO_D = 0x08
    SERVO_ALL = 0x0F
    def servo_set_positions(self,pos1,pos2,pos3,pos4, mask=SERVO_ALL):
        pkt = build_packet([RobotArmConn.CMD_UPDATE_SERVO_POSITION,pos1,pos2,pos3,pos4,mask])
        self.robot_conn.write(pkt)
        
    # High level Commands

    
    def __wait_for_idle(self):    
        print("Waiting for idle")
        mode = -1    
        while mode != 0:
            tmy = self.request_tmy()
            mode = tmy[RobotArmConn.TMY_PARAM_MODE]            
            if mode != 0:
                time.sleep(0.5)        
        print("Mode:", mode)                
        
    def __sync_command(self,cmd_fn, args, attempts=5):
        self.__wait_for_idle()
        command_accepted = False
        print("Starting command loop")
        while not command_accepted and attempts>0:
            #print("Attempt #",attempts)
            tmy_before = self.request_tmy()
            #parse_tmy(tmy_before)
            #print("Executing command")
            cmd_fn(*args)        
            time.sleep(1)
            tmy_after = self.request_tmy()
            #parse_tmy(tmy_after)
            command_accepted = (tmy_after[0] == (tmy_before[0]+1)) and (tmy_after[3] == 0)
            if not command_accepted:
                if attempts>0:
                    attempts-=1
                    time.sleep(1)

        if not command_accepted:
            print("Command rejected. ", tmy_before[0], tmy_after[0], "Cause:", tmy_after[3])
            raise ValueError("Command error")
            
            
    def open_claw(self):
        self.__sync_command(
            cmd_fn = self.servo_set_positions,
            args = (0,0,0,180, RobotArmConn.SERVO_D)
        )

    def close_claw(self):
        self.__sync_command(
            cmd_fn = self.servo_set_positions,
            args = (0,0,0,84, RobotArmConn.SERVO_D)
        ) 
        
    def rotate(self,angle):
        self.__sync_command(
            cmd_fn = self.servo_set_positions,
            args = (90-angle,0,0,84, RobotArmConn.SERVO_A)
        ) 

    def idle(self):
        self.__sync_command(
            cmd_fn = self.servo_set_positions,
            args = (90,90,130,90)
        ) 
        
    def arm_idle(self):
        self.__sync_command(
            cmd_fn = self.servo_set_positions,
            args = (0,90,130,0, RobotArmConn.SERVO_B|RobotArmConn.SERVO_C)   
        ) 
        
    def arm_collect_from_ground(self):
        self.__sync_command(
            cmd_fn = self.servo_set_positions,
            args = (0,152,56,0, RobotArmConn.SERVO_B|RobotArmConn.SERVO_C)   
        ) 
        
tmydef = {
    "params": [
        ("TMY_PARAM_ACCEPTED_PACKETS","int"),
        ("TMY_PARAM_REJECTED_PACKETS","int"),        
        ("TMY_PARAM_LAST_OPCODE","hex"),
        ("TMY_PARAM_LAST_ERROR","enum", "error_descriptions"),
        ("TMY_PARAM_MODE","enum", "mode_descriptions"),
        ("TMY_PARAM_SERVO1_POSITION","int"),
        ("TMY_PARAM_SERVO1_TARGET_POSITION","int"),
        ("TMY_PARAM_SERVO2_POSITION","int"),
        ("TMY_PARAM_SERVO2_TARGET_POSITION","int"),
        ("TMY_PARAM_SERVO3_POSITION","int"),
        ("TMY_PARAM_SERVO3_TARGET_POSITION","int"),
        ("TMY_PARAM_SERVO4_POSITION","int"),
        ("TMY_PARAM_SERVO4_TARGET_POSITION","int"),
    ],
    "enums": {
         "error_descriptions": {
              0: "success",
              1: "bad_sync",
              2: "invalid_length",
              3: "bad_crc",
              4: "bad_terminator",
              5: "timeout",
              6: "invalid_parameter",
              7: "invalid_mode"
        },
        "mode_descriptions": {
              0: "idle",
              1: "moving"
        }   
    }
}

def parse_tmy(tmybytes):    
    global tmydef
    i = 0
    for x in tmybytes[:-1]:
        if tmydef["params"][i][1] == 'int':
            print("%s: %d" % (tmydef["params"][i][0], x) )
        elif tmydef["params"][i][1] == 'hex':
            print("%s: 0x%02x" % (tmydef["params"][i][0], x) )
        elif tmydef["params"][i][1] == 'enum':
            print("%s: %s" % (
                tmydef["params"][i][0], 
                tmydef["enums"][tmydef["params"][i][2]][x]
            ) )
        i = i + 1    
    return        

import ipywidgets as widgets

class RobotArmGUI:
    def __init__(self,robot):
        self.robot = robot        
        
        self.bn_led_on = widgets.Button(
                description='LED ON',
                disabled=False,
                button_style='', # 'success', 'info', 'warning', 'danger' or ''
                tooltip='Turn on led'
        )
        self.bn_led_on.on_click(self.on_led_on_clicked)        
        self.bn_led_off = widgets.Button(
                description='LED OFF',
                disabled=False,
                button_style='', # 'success', 'info', 'warning', 'danger' or ''
                tooltip='Turn on led'
        )
        self.bn_led_off.on_click(self.on_led_off_clicked)        
        
        servo_positions_tmy_start = 4
        tmy_params_per_servo = 2
        
        tmy = self.robot.request_tmy()
        self.servo_positions = [
            tmy[servo_positions_tmy_start+0*tmy_params_per_servo],
            tmy[servo_positions_tmy_start+1*tmy_params_per_servo],
            tmy[servo_positions_tmy_start+2*tmy_params_per_servo],
            tmy[servo_positions_tmy_start+3*tmy_params_per_servo]
        ]        
        
        self.servo_sliders = [
            
            widgets.IntSlider( 
                value=self.servo_positions[0], 
                min=0, max=180,step=1,
                description='Servo A (Base):',
                disabled=False,
                continuous_update=False, 
                orientation='horizontal', 
                readout=True, 
                readout_format='d' 
            ),
            
            widgets.IntSlider( 
                value=self.servo_positions[1], 
                min=0, max=180,step=1,
                description='Servo B (Arm 1):',
                disabled=False,
                continuous_update=False, 
                orientation='horizontal', 
                readout=True, 
                readout_format='d' 
            ),
            
            widgets.IntSlider( 
                value=self.servo_positions[2], 
                min=0, max=180,step=1,
                description='Servo C (Arm 2):',
                disabled=False,
                continuous_update=False, 
                orientation='horizontal', 
                readout=True, 
                readout_format='d' 
            ),
            
            widgets.IntSlider( 
                value=self.servo_positions[3], 
                min=0, max=180,step=1,
                description='Servo C (Tool):',
                disabled=False,
                continuous_update=False, 
                orientation='horizontal', 
                readout=True, 
                readout_format='d' 
            ),
        ]
        pass
    
    def display(self):
        display(self.bn_led_on)
        display(self.bn_led_off)
        
        for s in self.servo_sliders:
            s.observe(self.on_servo_pos_changed, names='value')
            display(s)
        
        
    # Hooks

    # LED ON
    def on_led_on_clicked(self,b):
        self.robot.led_on()
        
    # LED OFF
    def on_led_off_clicked(self,b):
        self.robot.led_off()
        

    def on_servo_pos_changed(self,s):
        self.servo_positions[0] = self.servo_sliders[0].value
        self.servo_positions[1] = self.servo_sliders[1].value
        self.servo_positions[2] = self.servo_sliders[2].value
        self.servo_positions[3] = self.servo_sliders[3].value
        self.robot.servo_set_positions(
            self.servo_positions[0],
            self.servo_positions[1],
            self.servo_positions[2],
            self.servo_positions[3],
            0x0F
        )