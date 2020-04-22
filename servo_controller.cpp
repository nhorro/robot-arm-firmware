#include "servo_controller.h"

multiservo_controller::multiservo_controller() 
	:
		current_mode(multiservo_controller::mode::idle)
{
	float v = 20.0;

	this->servo_states[0].pin = SERVO_A_PIN;
	this->servo_states[0].x = 90.0;
	this->servo_states[0].x0 = 5;
	this->servo_states[0].x1 = 175;
	this->servo_states[0].v = v;

	this->servo_states[1].pin = SERVO_B_PIN;
	this->servo_states[1].x = 90.0;
	this->servo_states[1].x0 = 5;
	this->servo_states[1].x1 = 175;
	this->servo_states[1].v = v;

	this->servo_states[2].pin = SERVO_C_PIN;
	this->servo_states[2].x = 130.0;
	this->servo_states[2].x0 = 5;
	this->servo_states[2].x1 = 175;
	this->servo_states[2].v = v;

	this->servo_states[3].pin = SERVO_D_PIN;
	this->servo_states[3].x = 90.0;
	this->servo_states[3].x0 = 5;
	this->servo_states[3].x1 = 175;
	this->servo_states[3].v = v;

}

void multiservo_controller::setup()
{
 	for(int i=0;i<4;i++)
	{		
		this->servo_states[i].target_x = this->servo_states[i].x;
    	this->servos[i].attach(servo_states[i].pin);
    	this->servos[i].write(servo_states[i].x);
  		this->servos[i].setEasingType(EASE_CUBIC_IN_OUT); // EASE_CIRCULAR_IN_OUT EASE_LINEAR
	} 
}

bool multiservo_controller::ease_to(const uint8_t* x) 
{  	
	if ( multiservo_controller::mode::idle != this->current_mode )
		return false;

	uint8_t mask = x[4];

	//setSpeedForAllServos(20);

	for(int i=0;i<4;i++)
	{	
		if(mask & (1<<i))
		{
			this->servo_states[i].target_x = static_cast<float>(x[i]);
			if (this->servo_states[i].target_x < this->servo_states[i].x0)
			{
				this->servo_states[i].target_x = this->servo_states[i].x0;
			}
			else if (this->servo_states[i].target_x > this->servo_states[i].x1)
			{
				this->servo_states[i].target_x = this->servo_states[i].x1;
			}

	    	this->servos[i].setEaseTo(this->servo_states[i].target_x,this->servo_states[i].v);			
		}
	} 	

	this->current_mode = multiservo_controller::mode::moving;		
	synchronizeAllServosAndStartInterrupt(false); // do not start interrupt

	return true;
}

void multiservo_controller::update() 
{	
	switch(this->current_mode)
	{
		case multiservo_controller::mode::idle:
		{
			delay(50);
		} break;

		case multiservo_controller::mode::moving:
		{
			if( updateAllServos() )
			{
				this->current_mode = multiservo_controller::mode::idle;				
			}
			else
			{
				delay(REFRESH_INTERVAL / 1000); // optional 20ms delay - REFRESH_INTERVAL is in Microseconds				
			}
		} break;
	}
}