/** microphone_fft.ino
 *  Author:       hi
 *  Date:         30.11.2012
 *  Description:  Use a microphone and
 *                write data on serial.
 *  
 *  Arduino pin A0 to AUD pin.
 */

#include <stdint.h>
#include <ffft.h>

#define AML 50 // AMBIENT_MAX_LED
#define AMBIENT_SLOWDOWN_FACTOR 2

#define AMBIENT_MAX_BASS_VOLUME 50
#define AMBIENT_MAX_VOLUME 25

#define BASS_THRESHOLD 100
#define ACCENT_THRESHOLD 125

#define BASS_MAX 5
#define MID_MAX 10

#define TREBLE_MIN 16
#define TREBLE_MAX 64

#define  IR_AUDIO  5 // Analog input pin of the microphone

#define REDPIN 5
#define GREENPIN 6
#define BLUEPIN 3

volatile  byte  position = 0;
volatile  long  zero = 0;

int16_t capture[FFT_N];			/* Wave captureing buffer */
complex_t bfly_buff[FFT_N];		/* FFT buffer */
uint16_t spectrum[FFT_N/2];		/* Spectrum output buffer */
uint16_t spectrumPrior[FFT_N/2]; // prior of spectrum
float levelsPrior[3];

int low_max = 0, mid_max = 0, high_max = 0;

typedef struct _RGB {
	byte r;
	byte g;
	byte b;
} RGB;

RGB led;
byte ambient_led = 0;
byte ambient_counter = 0;

void setup()
{
	boot();
	Serial.begin(57600);
	adcInit();
	adcCalb();
}
int accentSkipCount = 0;
void loop()
{
	if (position == FFT_N) {
		fft_input(capture, bfly_buff);
		fft_execute(bfly_buff);
		fft_output(bfly_buff, spectrum);
		
		graph();
		if (at_ambient_levels()) {
			fade_ambient();
			low_max = 0;
			mid_max = 0;
			high_max = 0;
		} else {
			if (bass_hit()) {
		 		setRGB(255, 255, 255);
			} else {
				if (accentSkipCount < 1) {
					byte accent_index = find_accent();
					if (accent_index != 0) {
				        if (accent_index < 6)
				            setRGB(0, 255, (accent_index-3)*85);
				        else if (accent_index < 9)
				            setRGB(0, (255-(accent_index-6)*85), 255);
				        else if (accent_index < 16)
				            setRGB(0, (accent_index-9)*51, 255);
				        else if (accent_index < 33)
				            setRGB((255-(accent_index-16)*15), 0, 255);
				        else
				            setRGB(255, (accent_index-33)*7, 0);
				    	accentSkipCount = 3;
					} else { 
						int low = 0, mid = 0, high = 0;
						int low_count = 0, mid_count = 0, high_count = 0;

						// average loop
						for (byte i = 2; i < 64; i++) {
							int s = spectrum[i];
							if (s > AMBIENT_MAX_VOLUME) {
								if (i < BASS_MAX) {
									low += s;
									low_count++;
								} else if (i < MID_MAX) {
									mid += s;
									mid_count++;
								} else {
									high += s;
									high_count++;
								}
							}	
						}

						low /= low_count;
						mid /= mid_count;
						high /= high_count;

						if (low > low_max) low_max = low;
						if (mid > mid_max) mid_max = mid;
						if (high > high_max) high_max = high;

						int frac_low = low * 255 / low_max;
						int frac_mid = mid * 255 / mid_max;
						int frac_high = high * 255 / high_max;
						
						setRGB(frac_high, frac_low, frac_mid);
					}
				} else accentSkipCount--;
			}
		}
		position = 0;
	}
}

void setRGB(int r, int g, int b)
{
	// sanitize inputs
	if (r < 0) r = 0; if (r > 255) r = 255;
	if (g < 0) g = 0; if (g > 255) g = 255;
	if (b < 0) b = 0; if (b > 255) b = 255;

	led.r = r;
	led.g = g;
	led.b = b;
	updateLights();
}

void updateLights()
{
	analogWrite(REDPIN, led.r);
	analogWrite(GREENPIN, led.g);
	analogWrite(BLUEPIN, led.b);
}

void turnOff()
{
	setRGB(0, 0, 0);
	updateLights();
}

void fade(int amt)
{
	if (led.r < amt) led.r = 0; else led.r -= amt;
	if (led.g < amt) led.g = 0; else led.g -= amt;
	if (led.b < amt) led.b = 0; else led.b -= amt;
	updateLights();
}

void boot()
{
	turnOff();
	setRGB(255, 0, 0);
	delay(500);
	setRGB(0, 255, 0);
	delay(500);
	setRGB(0, 0, 255);
	delay(500);
	turnOff();
}

void graph()
{
	for (byte i = 0; i < 64; i++) {
		Serial.print(spectrum[i]);
		Serial.print('\t');
	}
	Serial.println();
}

bool at_ambient_levels()
{
	for (byte i = 0; i < 2; i++)
		if (spectrum[i] > AMBIENT_MAX_BASS_VOLUME) return false;
	for (byte i = 2; i < 64; i++)
		if (spectrum[i] > AMBIENT_MAX_VOLUME) return false;
	return true;
}

void fade_ambient()
{
	if (ambient_led < AML)
		setRGB(0, AML, ambient_led); // green to cyan
	else if (ambient_led < AML*2)
		setRGB(0, AML*2 - ambient_led, AML); // cyan to blue
	else if (ambient_led < AML*3)
		setRGB(ambient_led - AML*2, 0, AML); // blue to magenta
	else if (ambient_led < AML*4)
		setRGB(AML, 0, AML*4 - ambient_led); // magenta to red
	else if (ambient_led < AML*5)
		setRGB(AML, ambient_led - AML*4, 0); // red to yellow
	else if (ambient_led < AML*6)
		setRGB(AML*6 - ambient_led, AML, 0); // yellow to green
	ambient_led = (ambient_led + 1) % (AML*6);
}

// currently returns last accent, may need to modify
byte find_accent()
{
	byte accent_index = 0;
	for (byte i = 3; i < 64; i++)
		if (spectrum[i] > ACCENT_THRESHOLD)
				accent_index = i;
	return accent_index;
}

bool bass_hit() 
{
	return spectrum[0] > BASS_THRESHOLD || spectrum[1] > BASS_THRESHOLD || spectrum[2] > BASS_THRESHOLD;
}

/**
 * Begin FFT functions
 */
ISR(ADC_vect)
{
	if (position >= FFT_N)
		return;

	capture[position] = ADC + zero;
	if (capture[position] == -1 || capture[position] == 1)
		capture[position] = 0;

	position++;
}

void adcInit()
{
	/**   REFS0 : VCC use as a ref, 
	 *    IR_AUDIO : channel selection, 
	 *    ADEN : ADC Enable, 
	 *    ADSC : ADC Start, 
	 *    ADATE : ADC Auto Trigger Enable, 
	 *    ADIE : ADC Interrupt Enable,  
	 *    ADPS : ADC Prescaler  
	 */
	
	// free running ADC mode, f = ( 16MHz / prescaler ) / 13 cycles per conversion 
	ADMUX = _BV(REFS0) | IR_AUDIO; // | _BV(ADLAR); 
	
	//  ADCSRA = _BV(ADSC) | _BV(ADEN) | _BV(ADATE) | _BV(ADIE) | _BV(ADPS2) | _BV(ADPS1) 
	//prescaler 64 : 19231 Hz - 300Hz per 64 divisions
	ADCSRA = _BV(ADSC) | _BV(ADEN) | _BV(ADATE) | _BV(ADIE) | _BV(ADPS2) | _BV(ADPS1) | _BV(ADPS0); 
	
	// prescaler 128 : 9615 Hz - 150 Hz per 64 divisions, better for most music
	sei();
}

void adcCalb()
{ 
	long midl = 0;
	// get 2 meashurment at 2 sec
	// on ADC input must be NO SIGNAL!!!
	for (byte i = 0; i < 2; i++) {
			position = 0;
			delay(100);
			midl += capture[0];
			delay(900);
	}
	zero = -midl/2;
}
/**
 * End FFT functions
 */