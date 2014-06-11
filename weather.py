import urllib2
import json
import time
from RPIO import PWM

LOCATION = '95125'
API_KEY = '13a60c975cb73047'

METER_SUPPLY_V = 12.3
METER_FULL_RANGE_V = 10.0
PWM_MAX = 20000
TEMP_MIN = 20
TEMP_MAX = 120
UPDATE_TIME_MINS = 30

servo = PWM.Servo(pulse_incr_us=1)

meterToGPIOMapping = {'Temp':9, 'Forecast':8, 'ForecastTemp':7}

forecastVoltageMapping = {
	'Sunny':0.1, 
	'Partly Cloudy':(0.25 * METER_FULL_RANGE_V),
	'Cloudy':(0.5 * METER_FULL_RANGE_V),
	'Light Rain':(0.75 * METER_FULL_RANGE_V),
	'Rain':METER_FULL_RANGE_V
	}
	
forecastMapping = {}
	
def fetchWeather(client):
	data = client.fetch_weather( client.fetch_woeid(LOCATION) )
	
	temp = data['condition']['temp']
	forecast = forecastMapping[data['forecast'][0]['code']]
	forecastTemp = data['forecast'][0]['high']
	
	return {'temp':temp, 'forecast':forecast, 'forecastTemp':forecastTemp}

def setPWM(gpio, val):
	print "Setting GPIO: " + str(gpio) + " to PWM val: " + str(val)
	servo.set_servo(gpio, val)

def setMeterVoltage(meter, voltage):
	if(voltage > METER_FULL_RANGE_V):
		voltage = METER_FULL_RANGE_V
		
	val = int(voltage * PWM_MAX / METER_SUPPLY_V + 0.5)
	setPWM(meterToGPIOMapping[meter], val)
	
def updateTempMeter(temp):
	temp = int(temp)
	
	if(temp < TEMP_MIN):
		temp = TEMP_MIN
	if(temp > TEMP_MAX):
		temp = TEMP_MAX
		
	print "Temp: " + str(temp)
	voltage = (temp - 20) * METER_FULL_RANGE_V / 100.0
	setMeterVoltage('Temp', voltage)

def updateForecastMeter(forecast):
	print "Forecast: " + forecast
	setMeterVoltage('Forecast',forecastVoltageMapping[forecast])
	
def updateForecastTempMeter(temp):
	temp = int(temp)
	
	if(temp < TEMP_MIN):
		temp = TEMP_MIN
	if(temp > TEMP_MAX):
		temp = TEMP_MAX
		
	print "Forecast Temp: " + str(temp)
	voltage = (temp - 20) * METER_FULL_RANGE_V / 100.0
	setMeterVoltage('ForecastTemp', voltage)
	
def main():
    
    while(1):
        try:
            f = urllib2.urlopen(
                'http://api.wunderground.com/api/' + API_KEY + '/forecast/conditions/q/' + LOCATION + '.json')
            
            json_string = f.read()
            parsed_json = json.loads(json_string)
            
            current_temp = parsed_json['current_observation']['temp_f']
            forecast_temp = parsed_json['forecast']['simpleforecast']['forecastday'][0]['high']['fahrenheit']
            
            f.close()

            updateTempMeter(current_temp)
            updateForecastMeter('Sunny')
            updateForecastTempMeter(forecast_temp)
            
            time.sleep(UPDATE_TIME_MINS * 60) # Sleep for 30 mins
            
        except urllib2.URLError:
        
            print "Network Error"
            time.sleep(10) # Retry in 10 seconds
            
if __name__ == "__main__":
	main()
