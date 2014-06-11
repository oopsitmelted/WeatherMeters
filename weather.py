import yweather;
import urllib2;
import time;
from RPIO import PWM;

LOCATION = 'San Jose, CA';

METER_SUPPLY_V = 12.3;
METER_FULL_RANGE_V = 10.0;
PWM_MAX = 20000;
TEMP_MIN = 20;
TEMP_MAX = 120;
UPDATE_TIME_MINS = 30;

servo = PWM.Servo(pulse_incr_us=1);

meterToGPIOMapping = {'Temp':9, 'Forecast':8, 'ForecastTemp':7};

forecastVoltageMapping = {
	'Sunny':0.1, 
	'Partly Cloudy':(0.25 * METER_FULL_RANGE_V),
	'Cloudy':(0.5 * METER_FULL_RANGE_V),
	'Light Rain':(0.75 * METER_FULL_RANGE_V),
	'Rain':METER_FULL_RANGE_V
	}
	
forecastMapping = {
	'0' 	:	'Rain'			,	# Tornado
	'1'		:	'Rain'			,	# Tropical Storm
	'2' 	:	'Rain'			, 	# Hurricane
	'3'		:	'Rain'			,	# Severe Thunderstorms
	'4'		:	'Rain'			,	# Thunderstorms
	'5'		:	'Rain'			,	# Mixed Rain and Snow
	'6' 	:	'Rain'			,	# Mixed Snow and Sleet
	'7'		:	'Rain'			,	# Mixed Rain and Sleet
	'8' 	:	'Light Rain'	,	# Freezing Drizzle
	'9' 	:	'Light Rain'	,	# Drizzle
	'10'	:	'Rain'			,	# Freezing Rain
	'11'	:	'Rain'			,	# Showers
	'12'	:	'Rain'			,	# Showers
	'13'	:	'Rain'			,	# Snow Flurries
	'14'	:	'Light Rain'	,	# Light Snow Showers
	'15'	:	'Rain'			,	# Blowing Snow
	'16'	:	'Rain'			,	# Snow
	'17'	:	'Rain'			,	# Hail
	'18'	:	'Rain'			,	# Sleet
	'19'	:	'Cloudy'		,	# Dust
	'20'	:	'Cloudy'		,	# Foggy
	'21'	:	'Cloudy'		,	# Haze
	'22'	:	'Cloudy'		,	# Smoky
	'23'	:	'Sunny'			,	# Blustery
	'24'	:	'Sunny'			,	# Windy
	'25'	:	'Sunny'			,	# Cold
	'26'	:	'Cloudy'		,	# Cloudy
	'27'	:	'Cloudy'		,	# Mostly Cloudy (night)
	'28'	:	'Cloudy'		,	# Mostly Cloudy (day)
	'29'	:	'Partly Cloudy'	,	# Partly Cloudy (night)
	'30'	:	'Partly Cloudy'	,	# Partly Cloudy (day)
	'31'	:	'Sunny'			,	# Clear (night)
	'32'	:	'Sunny'			,	# Sunny
	'33'	:	'Sunny'			,	# Fair (night)
	'34'	:	'Sunny' 		,	# Fair (day)
	'35'	:	'Rain'			,	# Mixed Rain and Hail 
	'36'	:	'Sunny'			,	# Hot
	'37'	:	'Rain'			,	# Isolated Thunderstorms
	'38'	:	'Light Rain'	,	# Scattered Thunderstorms
	'39'	:	'Light Rain'	,	# Scattered Thunderstorms
	'40'	:	'Light Rain'	,	# Scattered Showers
	'41'	:	'Rain'			,	# Heavy Snow
	'42'	:	'Rain'			,	# Scattered Snow Showers
	'43'	:	'Rain'			,	# Heavy Snow
	'44'	:	'Partly Cloudy'	,	# Partly Cloudy
	'45'	:	'Rain'			,	# Thunderstorms
	'46'	:	'Rain'			,	# Snow Showers
	'47'	:	'Light Rain'		# Isolated Thundershowers 
	}
	
def fetchWeather(client):
	data = client.fetch_weather( client.fetch_woeid(LOCATION) );
	
	temp = data['condition']['temp'];
	forecast = forecastMapping[data['forecast'][0]['code']];
	forecastTemp = data['forecast'][0]['high'];
	
	return {'temp':temp, 'forecast':forecast, 'forecastTemp':forecastTemp};

def setPWM(gpio, val):
	print "Setting GPIO: " + str(gpio) + " to PWM val: " + str(val);
	servo.set_servo(gpio, val);

def setMeterVoltage(meter, voltage):
	if(voltage > METER_FULL_RANGE_V):
		voltage = METER_FULL_RANGE_V;
		
	val = int(voltage * PWM_MAX / METER_SUPPLY_V + 0.5);
	setPWM(meterToGPIOMapping[meter], val);
	
def updateTempMeter(temp):
	temp = int(temp);
	
	if(temp < TEMP_MIN):
		temp = TEMP_MIN;
	if(temp > TEMP_MAX):
		temp = TEMP_MAX;
		
	print "Temp: " + str(temp);
	voltage = (temp - 20) * METER_FULL_RANGE_V / 100.0; 
	setMeterVoltage('Temp', voltage);

def updateForecastMeter(forecast):
	print "Forecast: " + forecast;
	setMeterVoltage('Forecast',forecastVoltageMapping[forecast]);
	
def updateForecastTempMeter(temp):
	temp = int(temp);
	
	if(temp < TEMP_MIN):
		temp = TEMP_MIN;
	if(temp > TEMP_MAX):
		temp = TEMP_MAX;
		
	print "Forecast Temp: " + str(temp);
	voltage = (temp - 20) * METER_FULL_RANGE_V / 100.0; 
	setMeterVoltage('ForecastTemp', voltage);
	
def main():
    
    while(1):
        try:
            client = yweather.Client();
            conditions = fetchWeather(client);
            
            updateTempMeter(conditions['temp']);
            updateForecastMeter(conditions['forecast']);
            updateForecastTempMeter(conditions['forecastTemp']);
            time.sleep(UPDATE_TIME_MINS * 60); # Sleep for 30 mins
        except urllib2.URLError:
            print "Network Error"
            time.sleep(10); # Retry in 10 seconds
            
if __name__ == "__main__":
	main();
