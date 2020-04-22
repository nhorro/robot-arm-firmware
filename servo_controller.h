#ifndef SERVO_CONTROLLER_H
#define SERVO_CONTROLLER_H

#include <Arduino.h>
//#include <Servo.h>
#include <ServoEasing.h>

#define SERVO_A_PIN 3
#define SERVO_B_PIN 4
#define SERVO_C_PIN 5
#define SERVO_D_PIN 6

#define SERVO_A_MSK = 0x01
#define SERVO_B_MSK = 0x02
#define SERVO_C_MSK = 0x04
#define SERVO_D_MSK = 0x08

struct servo_descriptor {
  int pin;  
  float x;
  float target_x;
  float x0;
  float x1;
  float v;
};


class multiservo_controller {
public:
    enum mode {
        idle = 0,
        moving = 1
    };

    multiservo_controller();
    void setup();
    bool ease_to(const uint8_t* x);
    const servo_descriptor* get_states() const { return this->servo_states; }
    void update();
    inline mode get_mode() const { return this->current_mode; }
private:
  ServoEasing servos[4];
  servo_descriptor servo_states[4];
  volatile mode current_mode;
};

#endif // SERVO_CONTROLLER_H