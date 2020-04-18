#ifndef BENCH_TEST_APPLICATION_H
#define BENCH_TEST_APPLICATION_H

#include <Arduino.h>
#include "protocol.h"
#include "servo_controller.h"

#include "cmd_def.h"
#include "tmy_def.h"

class application: public protocol::packet_decoder
{
public:
	application();
	void setup();
	void process();

private:
	uint8_t tmy[TMY_PARAM_LAST];

	/* devices */
	multiservo_controller servo_ctrl;

	using opcode_callback = application::error_code(application::*)(const char* payload, uint8_t n);
	opcode_callback opcode_callbacks[OPCODE_LAST];

	/* Commands :: System commands */
	application::error_code application::request_tmy(const char* payload,
			uint8_t n);
	application::error_code application::led_on(const char* payload, uint8_t n);
	application::error_code application::led_off(const char* payload,
			uint8_t n);

	application::error_code application::echo(const char* payload,
			uint8_t n);	

	/* Commands :: Servo control commands */
	application::error_code application::update_servo_positions(
			const char* payload, uint8_t n);


	/* required by packet_decoder */
	void process_payload(const char* payload, uint8_t n) override;
	void set_error(error_code ec) override;
};

#endif // BENCH_TEST_APPLICATION_H
