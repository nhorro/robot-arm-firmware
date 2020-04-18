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
    CMD_REQUEST_TMY = 0
    CMD_LED_ON = 1
    CMD_LED_OFF = 2
    CMD_ECHO = 3
    CMD_UPDATE_SERVO_POSITION = 4
    
    def __init__(self, port=DEFAULT_SERIAL_PORT, baudrate=DEFAULT_BAUDRATE):
        self.port = port
        self.baudrate=baudrate
        self.robot_conn = None
                
    def connect(self):
        self.robot_conn = serial.Serial( self.port, self.baudrate,timeout=1)
        
    def disconnect(self):
        self.robot_conn.close()
        
    # Basic Protocol Leds and TMY
    def request_tmy(self):
        pkt = build_packet([RobotArmConn.CMD_REQUEST_TMY])
        self.robot_conn.write(pkt)
        return self.robot_conn.readline()
    
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
    def servo_set_positions(self,pos1,pos2,pos3,pos4):
        pkt = build_packet([RobotArmConn.CMD_UPDATE_SERVO_POSITION,pos1,pos2,pos3,pos4])
        self.robot_conn.write(pkt)
        
tmydef = {
    "params": [
        ("TMY_PARAM_ACCEPTED_PACKETS","int"),
        ("TMY_PARAM_REJECTED_PACKETS","int"),
        ("TMY_PARAM_LAST_OPCODE","hex"),
        ("TMY_PARAM_LAST_ERROR","enum", "error_descriptions"),
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
              5: "timeout"
        }   
    }
}

def parse_tmy(tmybytes):    
    global tmydef
    assert(len(tmybytes) == (len(tmydef["params"])+1) )
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
            self.servo_positions[3]
        )