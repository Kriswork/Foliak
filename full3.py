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
max_value_asC=38000

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
sensor = digitalio.DigitalInOut(board.D7)

# File to store data
file_path = "nawodnienie_zapis.txt"

# Ensure file exists before appending
try:
    with open(file_path, "x") as file:
        file.write("Data\tGodzina\tNapięcie(V)_C_(P0)\tRAW_C_(P0)\tProcent_C_(P0)\tNapięcie(V)_R_(P7)\tRAW_R_(P7)\tProcent_R_(P7)\tProg_(bool)\n")
except FileExistsError:
    pass

time.sleep(1)

while True:
    # create an analog input channel on pin: 0
    chan7 = AnalogIn(mcp, MCP.P7)
    chan0 = AnalogIn(mcp, MCP.P0)
    
    # Read analog voltage and raw value from GPIO7
    d7 = sensor.value # wartość bool wyjście D0 czyjnik wilgotności 
    ap0_voltage = chan0.voltage # wartość w Voltach pin analgowy 0 (MCP3008)
    ap0_raw = chan0.value  # wartość raw pin analgowy 0 (MCP3008)
    ap7_voltage = chan7.voltage # wartość w Voltach pin analgowy 7 (MCP3008)
    ap7_raw = chan7.value # wartość raw pin analgowy 7 (MCP3008)
    
  
    # Get current date and time
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    
    # Format data for logging
    log_entry = f"{date_str}\t{time_str}\t{ap0_voltage:.2f}\t{ap0_raw}\t{sensor_to_percentage(ap0_raw, min_value_asC, max_value_asC)}%\t{ap7_voltage:.2f}\t{ap7_raw}\t{sensor_to_percentage(ap7_raw, min_value_asR, max_value_asR)}%\t{d7}\n"
    
    # Write to file
    with open(file_path, "a") as file:
        file.write(log_entry)
    
    # print(log_entry.strip())
    time.sleep(1800)


