import machine

level_sensor_adc = machine.ADC(machine.Pin(28))  

logging_timer = machine.Timer() # type: ignore


DATA_IIR_CONST = 10_000
depth = 0 #Current measured IIR depth

def logDataWifi(Timer):
    print('Depth:', depth)


logging_timer.init(mode=machine.Timer.PERIODIC,period=1_000,callback=logDataWifi) 

# in ADC code
# Zero Depth Code: 12000
# 30" depth: 18335, for a depth coefficient of 0.004735

#Depth testing
# Off depth: 5"


while True: #Main loop, just take measurments
    depth = (level_sensor_adc.read_u16() - 12000) * 0.004735 / DATA_IIR_CONST + depth * (DATA_IIR_CONST - 1) / DATA_IIR_CONST