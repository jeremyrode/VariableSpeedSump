"""Example script.

Edit the I2C interface constant to match the one you have
connected the sensor to.
"""

from ina219 import INA219
import machine

SHUNT_OHMS = 0.1

i2c = machine.I2C(0, scl=machine.Pin(1), sda=machine.Pin(0))

ina = INA219(SHUNT_OHMS, i2c)
ina.configure()
print("Bus Voltage: %.3f V" % ina.voltage())
print("Current: %.3f mA" % ina.current())
print("Power: %.3f mW" % ina.power())
