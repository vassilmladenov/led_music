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
 
#define BASS_MIN 0
#define BASS_MAX 5

#define MID_MIN 5
#define MID_MAX 16

#define TREBLE_MIN 16
#define TREBLE_MAX 64

#define  IR_AUDIO  5 // ADC channel to capture

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

typedef struct _RGB {
	byte r;
	byte g;
	byte b;
} RGB;

RGB led;



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
		
		// if (spectrum[0] < 400) {
		// if (accentSkipCount == 0) {
		// int bass = 0, mid = 0, treble = 0;
		// int bassCount = 0, midCount = 0, trebleCount = 0;
		// if (spectrum[0] < 20 && spectrum[1] < 20) {
			graph();
			if (spectrum[0] > 160 && spectrum[0]-spectrum[1] > 40) {
				setRGB(255, 255, 255);
			} else {
				byte peak = 2;
				for (byte i = 2; i < 41; i++) {
					if (spectrum[i] > 80 && spectrum[i] > spectrum[i-1] && spectrum[i] > spectrum[i+1]) peak = i;
				}
				// if (peak != 0) {
				if (peak < 21) {
					setRGB(255 - 25*peak, 25*peak,0);
				} else {
				 	peak -= 20;
					setRGB(0, 255 - 25*peak, 25*peak);
				}
			}
		// }
		// }
			// // average loop
			// for (byte i = 0; i < 64; i++) {
			// 	int s = spectrum[i];
			// 	if (s > 30) {
			// 		if (i < BASS_MAX) {
			// 			bass += s;
			// 			bassCount++;
			// 		} else if (i < MID_MAX) {
			// 			mid += s;
			// 			midCount++;
			// 		} else {
			// 			treble += s;
			// 			trebleCount++;
			// 		}
			// 	}	
			// }

			// bass = bass / bassCount;
			// mid /= midCount;
			// treble /= trebleCount;

			// if (bass < mid) { // remove lowest
			// 	if (bass < treble) bass = 0;
			// 	else treble = 0;
			// } else {
			// 	if (mid < treble) mid = 0;
			// 	else treble = 0;
			// }
			// int sum = bass + mid + treble;

			// int fracBass = bass * 255 / sum;
			// int fracMid = mid * 255 / sum;
			// int fracTreble = treble * 255 / sum;
			
			// setRGB(fracTreble, fracMid, fracBass);
			// setRGB(bass, mid, treble);
			// accentSkipCount = 5;
		// }
		// accentSkipCount--;
		position = 0;
	// }
	}
	// if (position % 10 == 0) fade(1);

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