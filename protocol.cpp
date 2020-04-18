#include "protocol.h"

namespace protocol {

packet_decoder::packet_decoder()
{
	this->reset();
}

void packet_decoder::process_packets()
{
	if (this->new_data_available)
	{
		this->new_data_available = false;
		switch (this->current_state)
		{
		case pkt_state::pkt_state_idle:
		{
			if (PACKET_SYNC_0_CHAR == this->last_received_char)
			{
				this->current_state =
						pkt_state::pkt_state_expecting_start_sync1;
			}
		}
			break;

		case pkt_state::pkt_state_expecting_start_sync1:
		{
			if (PACKET_SYNC_1_CHAR == this->last_received_char)
			{
				this->current_state =
						pkt_state::pkt_state_expecting_start_sync2;
			}
			else
			{
				this->set_error(error_code::bad_sync);
				this->reset();
			}
		}
			break;

		case pkt_state::pkt_state_expecting_start_sync2:
		{
			if (PACKET_SYNC_2_CHAR == this->last_received_char)
			{
				this->current_state =
						pkt_state::pkt_state_expecting_start_sync3;
			}
			else
			{
				this->set_error(error_code::bad_sync);
				this->reset();
			}
		}
			break;

		case pkt_state::pkt_state_expecting_start_sync3:
		{
			if (PACKET_SYNC_3_CHAR == this->last_received_char)
			{
				this->current_state = pkt_state::pkt_state_expecting_length;
			}
			else
			{
				this->set_error(error_code::bad_sync);
				this->reset();
			}
		}
			break;

		case pkt_state::pkt_state_expecting_length:
		{
			this->payload_length = this->last_received_char;
			if (this->payload_length
					&& (this->payload_length <= PAYLOAD_BUFFER_SIZE))
			{
				this->current_state = pkt_state::pkt_state_expecting_payload;
			}
			else
			{
				this->set_error(error_code::invalid_length);
				this->reset();
			}
		}
			break;

		case pkt_state::pkt_state_expecting_payload:
		{
			this->received_payload_buffer[this->received_payload_index] =
					this->last_received_char;
			if (++this->received_payload_index == this->payload_length)
			{
				this->expected_crc16 = calc_crc16(
						this->received_payload_buffer,
						this->received_payload_index);
				this->received_payload_buffer[this->received_payload_index] =
						'\0';
				this->current_state = pkt_state::pkt_state_expecting_crc1;
			}
		}
			break;

		case pkt_state::pkt_state_expecting_crc1:
		{
			this->crc16 = this->last_received_char << 8;
			this->current_state = pkt_state::pkt_state_expecting_crc2;
		}
			break;

		case pkt_state::pkt_state_expecting_crc2:
		{
			this->crc16 |= this->last_received_char;

			if (this->expected_crc16 == this->crc16)
			{
				this->current_state = pkt_state::pkt_state_expecting_terminator;
			}
			else
			{
				this->set_error(error_code::bad_crc);
				this->reset();
			}

		}
			break;

		case pkt_state::pkt_state_expecting_terminator:
		{
			if (PACKET_TERMINATOR_CHAR == this->last_received_char)
			{
				this->process_payload(this->received_payload_buffer,
						this->received_payload_index);
			}
			else
			{
				this->set_error(error_code::bad_terminator);
			}
			this->reset();
		}
			break; 
		}
	} // end switch
	else
	{ // timeout
		if (++this->iteration_counter == cmd_timeout)
		{
			this->reset();
		}
	}
}

void packet_decoder::reset()
{
	this->current_state = pkt_state::pkt_state_idle;
	this->received_payload_index = 0;
	this->iteration_counter = 0;
	this->crc16 = 0;
}

uint16_t calc_crc16(const unsigned char* data_p, uint8_t length)
{
	uint8_t x;
	uint16_t crc = 0xFFFF;
	while (length--)
	{
		x = crc >> 8 ^ *data_p++;
		x ^= x >> 4;
		crc = (crc << 8) ^ ((uint16_t)(x << 12)) ^ ((uint16_t)(x << 5))
				^ ((uint16_t) x);
	}
	return crc;
}

} // namespace packets
