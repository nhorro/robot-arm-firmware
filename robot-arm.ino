#include <Arduino.h>
#include "application.h"

#define APP_SERIAL_BAUDRATE 115200

static application app;

static void setup_serial_input()
{
	// Open serial communications and wait for port to open:
	Serial.begin(APP_SERIAL_BAUDRATE);
	while (!Serial)
	{
		; // wait for serial port to connect. Needed for native USB port only
	}
}

void setup() 
{   
  setup_serial_input();
  app.setup();
}

void loop() 
{  
  /* Read commands */
  if (Serial.available() > 0)
  {
  	app.feed(Serial.read());
  }
  app.process();  
}
