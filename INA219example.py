"""Example script.

Edit the I2C interface constant to match the one you have
connected the sensor to.
"""

from ina219 import INA219
import machine

SHUNT_OHMS = 0.05

i2c = machine.I2C(0, scl=machine.Pin(5), sda=machine.Pin(4))
logging_timer = machine.Timer() # type: ignore

ina = INA219(SHUNT_OHMS, i2c)
ina.configure()
power = 0
current = 0
voltage = 0
DATA_IIR_CONST = 5

def logDataWifi(Timer):
    print("Bus Voltage: %.3f V" % voltage)
    print("Current: %.3f mA" % current)
    print("Power: %.3f W" % power)


logging_timer.init(mode=machine.Timer.PERIODIC,period=1_000,callback=logDataWifi) 

while True: #Main loop, just take measurments
    power = ina.power() / 1_000 / DATA_IIR_CONST + power  * (DATA_IIR_CONST - 1) / DATA_IIR_CONST
    current = ina.current() / DATA_IIR_CONST + current  * (DATA_IIR_CONST - 1) / DATA_IIR_CONST
    voltage = ina.voltage() / DATA_IIR_CONST + voltage  * (DATA_IIR_CONST - 1) / DATA_IIR_CONST

