#include "application.h"

application::application() :
		opcode_callbacks
		{ 
			&application::request_tmy, 
			&application::led_on,
			&application::led_off,
			&application::echo,
			&application::update_servo_positions 
		}
{

}

void application::setup()
{
	pinMode(LED_BUILTIN, OUTPUT);

	// Servos
	this->servo_ctrl.setup();
}

void application::process()
{
	this->process_packets();
	this->servo_ctrl.update();
}

void application::process_payload(const char* payload, uint8_t n)
{

	uint8_t opcode = payload[0];
	if (OPCODE_REQUEST_TMY == opcode)
	{
		this->request_tmy(payload, n);
	}
	else
	{
		this->tmy[TMY_PARAM_ACCEPTED_PACKETS]++;
		this->tmy[TMY_PARAM_LAST_ERROR] =
				(opcode < OPCODE_LAST) ?
						(this->*(opcode_callbacks[opcode]))(payload + 1,
								n - 1) :
						error_code::unknown_opcode;
		this->tmy[TMY_PARAM_LAST_OPCODE] = static_cast<uint8_t>(opcode);
	}
}

void application::set_error(error_code ec)
{
	if (packet_decoder::error_code::timeout != ec)
	{
		this->tmy[TMY_PARAM_REJECTED_PACKETS]++;
		this->tmy[TMY_PARAM_LAST_ERROR] = static_cast<uint8_t>(ec);
	}
}

/* Opcodes */

application::error_code application::request_tmy(const char* payload, uint8_t n)
{
	this->tmy[TMY_PARAM_MODE] = static_cast<char>(this->servo_ctrl.get_mode());
	this->tmy[TMY_PARAM_SERVO1_CURR_POSITION] = static_cast<char>(this->servo_ctrl.get_states()[0].x);
	this->tmy[TMY_PARAM_SERVO1_TARGET_POSITION] = static_cast<char>(this->servo_ctrl.get_states()[0].target_x);
	this->tmy[TMY_PARAM_SERVO2_CURR_POSITION] = static_cast<char>(this->servo_ctrl.get_states()[1].x);
	this->tmy[TMY_PARAM_SERVO2_TARGET_POSITION] = static_cast<char>(this->servo_ctrl.get_states()[1].target_x);
	this->tmy[TMY_PARAM_SERVO3_CURR_POSITION] = static_cast<char>(this->servo_ctrl.get_states()[2].x);
	this->tmy[TMY_PARAM_SERVO3_TARGET_POSITION] = static_cast<char>(this->servo_ctrl.get_states()[2].target_x);
	this->tmy[TMY_PARAM_SERVO4_CURR_POSITION] = static_cast<char>(this->servo_ctrl.get_states()[3].x);
	this->tmy[TMY_PARAM_SERVO4_TARGET_POSITION] = static_cast<char>(this->servo_ctrl.get_states()[3].target_x);

	Serial.write(this->tmy, TMY_PARAM_LAST);
	Serial.write('\n');
	return error_code::success;
}

application::error_code application::led_on(const char* payload, uint8_t n)
{
	digitalWrite(LED_BUILTIN, HIGH);
	return error_code::success;
}

application::error_code application::led_off(const char* payload, uint8_t n)
{
	digitalWrite(LED_BUILTIN, LOW);
	return error_code::success;
}

application::error_code application::echo(const char* payload, uint8_t n)
{
	Serial.write(payload, n);
	return error_code::success;
}

application::error_code application::update_servo_positions(const char* payload,
		uint8_t n)
{		
	return this->servo_ctrl.ease_to(payload) ? error_code::success : error_code::invalid_mode;
}
