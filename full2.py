import busio
import digitalio
import board
import time
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from datetime import datetime

min_value_asR=22000
max_value_asR=65525
min_value_asC=18129
max_value_asC=44715

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

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# configure GPIO7 as analog input via MCP3008
sensor = AnalogIn(mcp, MCP.P7)

# File to store data
file_path = "nawodnienie_zapis.txt"

# Ensure file exists before appending
try:
    with open(file_path, "x") as file:
        file.write("Data\tGodzina\tNapięcie_P0\tRAW_P0\tProcent_P0\tNapięcie_P7\tRAW_P7\tProcent_P7\tNapięcie_GPIO7\tRAW_GPIO7\tProcent_GPIO7\n")
except FileExistsError:
    pass

time.sleep(1)

while True:
    # create an analog input channel on pin: 0
    chan7 = AnalogIn(mcp, MCP.P7)
    chan0 = AnalogIn(mcp, MCP.P0)
    
    # Read analog voltage and raw value from GPIO7
    sensor_voltage = sensor.voltage
    sensor_raw = sensor.value
    as0_voltage = chan0.voltage
    as0_raw = chan0.value
    as7_voltage = chan7.voltage
    as7_raw = chan7.value 
    
    # print(f"Wartość {as0_raw} -> {sensor_to_percentage(as0_raw, min_value_asR, max_value_asR)}%")
  
    # Get current date and time
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    
    # Format data for logging
    log_entry = f"{date_str}\t{time_str}\t{chan0.voltage:.2f}\t{chan0.value}\t{sensor_to_percentage(chan0.value, min_value_asC, max_value_asC)}%\t{chan7.voltage:.2f}\t{chan7.value}\t{sensor_to_percentage(as7_raw, min_value_asR, max_value_asR)}%\t{sensor_voltage:.2f}\t{sensor_raw}\t{sensor_to_percentage(sensor_raw, min_value_asR, max_value_asR)}%\n"
    
    # Write to file
    with open(file_path, "a") as file:
        file.write(log_entry)
    
    # print(log_entry.strip())
    time.sleep(1800)


