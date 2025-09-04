import time
import machine
import rp2
import network
import secrets
import urequests as requests
import ujson

print('boot')
## GPIO Setup for pump buttons
power_button = machine.Pin(15, mode=machine.Pin.OUT, pull=None, value=0)    # type: ignore
pause_button = machine.Pin(12, mode=machine.Pin.OUT, pull=None, value=0)    # type: ignore
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
log_retry_timer = machine.Timer() # type: ignore
# WLAN Setup
wlan = network.WLAN(network.STA_IF)
# Globals
DATA_IIR_CONST = 1000  # Filtering constant for the IIR filters
depth = 0 #Current measured IIR depth
depth_max = 10
depth_min = 5

def all_buttons_off():
    power_button.value(0)
    pause_button.value(0)
    up_button.value(0)
    down_button.value(0)

def button_delay(): #Call this after a button press
    button_press_timer.init(mode=machine.Timer.ONE_SHOT,period=600_000,callback=all_buttons_off) # type: ignore 
    
# Logging Function via Wifi
def logDataWifi():
    data = {"key1": "value1", "key2": 123} # Take the data
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
        if not wlan.isconnected():
            log_retry_timer.init(mode=machine.Timer.ONE_SHOT,period=2_000,callback=all_buttons_off)
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


def pumpSpeedFeedback():
    if depth > depth_max:  # If depth greater than upper target
        up_button.value(1) # Speed the pump up
        button_delay()
    elif depth < depth_min: # If depth greater than lower target (Will this go into pause mode??)
        down_button.value(1) # Slow the pump down
        button_delay()

# Start up the timers
logging_timer.init(mode=machine.Timer.PERIODIC,period=900_000,callback=logDataWifi)
feedback_loop_timer.init(mode=machine.Timer.PERIODIC,period=10_000,callback=pumpSpeedFeedback)

while True: #Main loop, just take measurments
    depth = level_sensor_adc.read_u16() / DATA_IIR_CONST + depth * (DATA_IIR_CONST - 1) / DATA_IIR_CONST 

