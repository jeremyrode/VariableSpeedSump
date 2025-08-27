import time
import machine
import rp2
import network
import secrets
import urequests as requests
import ujson

print('boot')
## GPIO Setup for pump buttons
power_button = machine.Pin(9, mode=machine.Pin.OUT, pull=None, value=0) # type: ignore
pause_button = machine.Pin(11, mode=machine.Pin.OUT, pull=None, value=0) # type: ignore
up_button = machine.Pin(14, mode=machine.Pin.OUT, pull=None, value=0) # type: ignore
down_button = machine.Pin(15, mode=machine.Pin.OUT, pull=None, value=0) # type: ignore
## ADC Setup
ct1_sensor_adc = machine.ADC(machine.Pin(26))     # 
ct2_sensor_adc = machine.ADC(machine.Pin(27))     #
level_sensor_adc = machine.ADC(machine.Pin(28))   # 
temp_sensor_adc = machine.ADC(4)
# Timers
button_press_timer = machine.Timer() # type: ignore
logging_timer = machine.Timer() # type: ignore
log_retry_timer = machine.Timer() # type: ignore
# WLAN Setup
wlan = network.WLAN(network.STA_IF)
# Globals
DATA_IIR_CONST = 1000  # Filtering constant for the IIR filters
level = 0 #
wifi_retry_counter = 0

def all_buttons_off():
    power_button.value(0)
    pause_button.value(0)
    up_button.value(0)
    down_button.value(0)

def button_delay(): #Call this after a button press
    button_press_timer.init(mode=machine.Timer.ONE_SHOT,period=600_000,callback=all_buttons_off) # type: ignore

def connectToWiFi():
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
    if not wlan.isconnected():
        log_retry_timer.init(mode=machine.Timer.ONE_SHOT,period=2_000,callback=all_buttons_off) # type: ignore
    print('\nIP Address: ', wlan.ifconfig()[0])


# Logging Function via Wifi
def logDataWifi():
    data = {"key1": "value1", "key2": 123} # Take the data
    if not wlan.isconnected():
        connectToWiFi()
    try:
        print("Trying to Post")
        res = requests.post(secrets.url, json = data) #What were sending
        print("Posted")
    except: #Need to catch this or we stop
        print("Log Failed, Post Error")
    else:
        if res.text != 'OK':
            print('Unexpected Post Response:', res.text)



# Start up the timers
logging_timer.init(mode=machine.Timer.PERIODIC,period=900_000,callback=logDataWifi) # type: ignore

while True: #Main loop, just take measurments
    level = level_sensor_adc.read_u16() / DATA_IIR_CONST + level * (DATA_IIR_CONST - 1) / DATA_IIR_CONST #Take Baseline Stats

