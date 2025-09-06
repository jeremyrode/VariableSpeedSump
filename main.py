import time
import machine
import rp2
import network
#import secrets
import urequests as requests
import ujson
import ina219

print('boot')
## GPIO Setup for pump buttons
power_button = machine.Pin(15, mode=machine.Pin.OUT, pull=None, value=0)    # type: ignore
pause_button = machine.Pin(9, mode=machine.Pin.OUT, pull=None, value=0)    # type: ignore
up_button = machine.Pin(11, mode=machine.Pin.OUT, pull=None, value=0)       # type: ignore
down_button = machine.Pin(14, mode=machine.Pin.OUT, pull=None, value=0)     # type: ignore
## ADC Setup
ct1_sensor_adc = machine.ADC(machine.Pin(26))    
ct2_sensor_adc = machine.ADC(machine.Pin(27))   
level_sensor_adc = machine.ADC(machine.Pin(28))  
temp_sensor_adc = machine.ADC(4)
# Timers
feedback_loop_timer = machine.Timer() # type: ignore
logging_timer = machine.Timer() # type: ignore
button_press_timer = machine.Timer() # type: ignore
# WLAN Setup
#wlan = network.WLAN(network.STA_IF)
# Globals
DATA_IIR_CONST = 1000  # Filtering constant for the IIR filters
depth = 0.0 #Current measured IIR depth
power = 0.0 #Measured Pump Power
disable_wifi_logging = True
upper_depth = 10 #Where the pump will speed up
mid_depth = 7 #Where the pump will slow
lower_depth = 5 #This is where air will be injested

def all_buttons_off(Timer):
    power_button.value(0)
    pause_button.value(0)
    up_button.value(0)
    down_button.value(0)

def button_delay(): #Call this after a button press
    button_press_timer.init(mode=machine.Timer.ONE_SHOT,period=200,callback=all_buttons_off) # type: ignore 

# Logging Function via Wifi
def logDataWifi(Timer):
    if disable_wifi_logging:
        print("Depth: %.3f" % depth)
        print("Power: %.3f W" % power)
    else:
        data = {"depth": depth, "power": power} # Take the data
        if not wlan.isconnected():
            print(f"Reconnecting to WiFi Network Name: {secrets.ssid}")
            try:
                wlan.active(True)
                wlan.connect(secrets.ssid, secrets.password)
            except OSError as error:
                print(f'Connect error is {error}')
            except Exception as e:
                print(f"An unkown connect error occurred: {e}")
                return
            print('Waiting for connection...')
            counter = 0
            while not wlan.isconnected():
                time.sleep(1)
                print(counter, '.', sep='', end='')
                counter += 1
                if counter > 20:
                    print('Failed to Connect')
                    return
            print('\nIP Address: ', wlan.ifconfig()[0])
            try:
                print("Trying to Post")
                res = requests.post(secrets.url, json = data) #What were sending
                print("Posted")
            except: #Need to catch this or we stop
                print("Log Failed, Post Error")
            else:
                if res.text != 'OK':
                    print('Unexpected Post Response:', res.text)


def pumpSpeedFeedback(Timer):
    if depth > upper_depth:  # If depth greater than upper target
        if power > 5:
            up_button.value(1) # Speed the pump up
            print('Speed Up')
        else:
            pause_button.value(1) #unpause
            print('Unpause')
        button_delay()
    elif depth > mid_depth: #We are lower then upper
        print('No speed changes')
    elif depth > lower_depth: # We are lower than mid
        down_button.value(1) # Slow the pump down, we can check speed state via power!
        print('Speed Down')
        button_delay()
    elif power > 5: # We are less than min and pump is still on!
        pause_button.value(1) # Go for pause
        print('Go for Pause')
        button_delay()
    else:
        print('Stay Paused')

print('Start Timers')
# Start up the timers
logging_timer.init(mode=machine.Timer.PERIODIC,period=2_000,callback=logDataWifi) # type: ignore
feedback_loop_timer.init(mode=machine.Timer.PERIODIC,period=10_000,callback=pumpSpeedFeedback) # type: ignore
# Setup Perepherials
i2c = machine.I2C(0, scl=machine.Pin(5), sda=machine.Pin(4))
ina = ina219.INA219(0.05, i2c)  # Used 2 x 0.1 ohms in parallel!
ina.configure()

print('Go Main Loop')
while True: #Main loop, just take measurments
    depth = (level_sensor_adc.read_u16() - 12000) * 0.004735 / DATA_IIR_CONST + depth * (DATA_IIR_CONST - 1) / DATA_IIR_CONST
    power = ina.power() / 1000 / DATA_IIR_CONST + power  * (DATA_IIR_CONST - 1) / DATA_IIR_CONST

