#ifndef PACKET_DECODER_H
#define PACKET_DECODER_H

#include <Arduino.h>

namespace protocol {

#define HEADER_SIZE 4
#define PAYLOAD_BUFFER_SIZE 64
#define TRAILER_SIZE (2+1)

const char PACKET_SYNC_0_CHAR = 'P';
const char PACKET_SYNC_1_CHAR = 'K';
const char PACKET_SYNC_2_CHAR = 'T';
const char PACKET_SYNC_3_CHAR = '!';
const char PACKET_TERMINATOR_CHAR = '\n';

class packet_decoder
{
public:
	const uint32_t cmd_timeout = 1000000;

	enum error_code
	{
		// Communication Protocol errors
		success = 0,
		bad_sync = 1,
		invalid_length = 2,
		bad_crc = 3,
		bad_terminator = 4,
		unknown_opcode = 5,
		timeout,

		// Application errors
		invalid_mode		
	};

	packet_decoder();

	inline void feed(uint8_t c)
	{
		this->last_received_char = c;
		this->new_data_available = true;
	}

	void process_packets();

	void reset();
	virtual void process_payload(const char* payload, uint8_t n) = 0;
	virtual void set_error(error_code ec) = 0;

private:
	enum class pkt_state
	{
		pkt_state_idle,
		pkt_state_expecting_start_sync1,
		pkt_state_expecting_start_sync2,
		pkt_state_expecting_start_sync3,
		pkt_state_expecting_length,
		pkt_state_expecting_payload,
		pkt_state_expecting_crc1,
		pkt_state_expecting_crc2,
		pkt_state_expecting_terminator
	};

	uint32_t iteration_counter;
	pkt_state current_state;
	char received_payload_buffer[PAYLOAD_BUFFER_SIZE + 1];
	uint8_t received_payload_index;
	uint16_t expected_crc16;
	uint16_t crc16;
	uint8_t last_received_char;
	bool new_data_available;
	uint8_t payload_length;
};

uint16_t calc_crc16(const unsigned char* data_p, uint8_t length);

class packet_encoder
{
public:
	packet_encoder() = default;

	inline void calc_crc_and_close_packet(uint8_t length)
	{
		uint16_t crc = calc_crc16(this->get_payload_buffer(), length);
		buffer[4 + length] = crc >> 8;
		buffer[4 + length + 1] = crc & 0xFF;
		buffer[4 + length + 2] = PACKET_TERMINATOR_CHAR;
	}

	inline char* get_payload_buffer()
	{
		return this->buffer + 4;
	}

	inline const char* get_packet() const
	{
		return this->buffer;
	}

private:
	uint8_t buffer[HEADER_SIZE+PAYLOAD_BUFFER_SIZE+TRAILER_SIZE];
};

} // namespace packets

#endif // PACKET_DECODER_H
