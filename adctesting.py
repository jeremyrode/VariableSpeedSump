import time
from machine import ADC, Pin

ct1_sensor_adc = ADC(Pin(26))     # create ADC object on ADC pin
ct2_sensor_adc = ADC(Pin(27))     # create ADC object on ADC pin
level_sensor_adc = ADC(Pin(28))     # create ADC object on ADC pin
temp_sensor_adc = ADC(4)

for i in range(50):
    print(level_sensor_adc.read_u16()) # read value, 0-65535 across voltage range 0.0v - 3.3v
    print(ct1_sensor_adc.read_u16())
    print(ct2_sensor_adc.read_u16())
    voltage = (3.3 / 65535) * temp_sensor_adc.read_u16()
    temperature_celsius = 27 - (voltage - 0.706) / 0.001721
    print(temperature_celsius)
    time.sleep_ms(500)      # sleep for 500 milliseconds