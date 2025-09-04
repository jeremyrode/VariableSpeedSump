import time
import machine

power_button = machine.Pin(15, mode=machine.Pin.OUT, pull=None, value=0)
pause_button = machine.Pin(12, mode=machine.Pin.OUT, pull=None, value=0)
up_button = machine.Pin(11, mode=machine.Pin.OUT, pull=None, value=0)
down_button = machine.Pin(14, mode=machine.Pin.OUT, pull=None, value=0)




up_button.value(1)
time.sleep_ms(500)      # sleep for 500 milliseconds
up_button.value(0)