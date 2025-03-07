import busio
import digitalio
import board
import time
import adafruit_mcp3xxx.mcp3008 as MCP
import adafruit_dht  # Biblioteka do obsługi DHT22
from adafruit_mcp3xxx.analog_in import AnalogIn
from datetime import datetime

dht_device = adafruit_dht.DHT22(board.D4)  # GPIO7 DHT22

min_value_asR=22000
max_value_asR=65525
min_value_asC=18129
max_value_asC=35000
min_value_asC2=18129
max_value_asC2=35000

def sensor_to_percentage(value, min_value, max_value):
    """
    Przekształca wartość sygnału czujnika na procenty.
    
    :param value: Odczytana wartość z czujnika
    :param min_value: Wartość odpowiadająca 100%
    :param max_value: Wartość odpowiadająca 0%
    :return: Wartość w procentach (0-100%)
    """
    if value > max_value:
        return 0.0
    elif value < min_value:
        return 100.0
    
    percentage = (max_value - value) / (max_value - min_value) * 100
    return round(percentage, 2)


# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D8)
print("cs D8: ", cs.value)
# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# configure GPIO7 as analog input via MCP3008


chan7 = AnalogIn(mcp, MCP.P7)
chan0 = AnalogIn(mcp, MCP.P0)
chan1 = AnalogIn(mcp, MCP.P1)
chan4 = AnalogIn(mcp, MCP.P4)
while True:

    
    temperature = dht_device.temperature
    humidity = dht_device.humidity
    
    # Read analog voltage and raw value from GPIO7
    as0_voltage = chan0.voltage
    as0_raw = chan0.value
    as1_voltage = chan1.voltage
    as1_raw = chan1.value
    as7_voltage = chan7.voltage
    as7_raw = chan7.value 
    print("")
    print(f"Temperatura: {temperature}, Wilgotność powietrze: {humidity}, Wartości rezystora: {chan4.value} -> {chan4.voltage}")
    print(f"Wartość rezystancyjna  {as7_raw} -> {as7_voltage:.2f}V -> {sensor_to_percentage(as7_raw, min_value_asR, max_value_asR)}%")
    print(f"Wartość pojemnosciowa  {as0_raw} -> {as0_voltage:.2f}V -> {sensor_to_percentage(as0_raw, min_value_asC, max_value_asC)}%")
    print(f"Wartość pojemnosciowa 2  {as1_raw} -> {as1_voltage:.2f}V -> {sensor_to_percentage(as1_raw, min_value_asC2, max_value_asC2)}%")
    print("")
    print("")
    

    time.sleep(3)


