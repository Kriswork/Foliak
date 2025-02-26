import digitalio
import board
import time
import BlynkLib  # Klient Blynk TCP
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from datetime import datetime

# KONFIGURACJA BLYNK
BLYNK_AUTH_TOKEN = "TWÓJ_TOKEN_BLYNK"
blynk = BlynkLib.Blynk(BLYNK_AUTH_TOKEN)

# Wirtualne piny w aplikacji Blynk
PIN_RESISTANCE = 1  # Odpowiada V1 w aplikacji Blynk
PIN_CAPACITANCE = 2  # Odpowiada V2

# KONFIGURACJA CZUJNIKÓW
min_value_asR=22000
max_value_asR=65525
min_value_asC=18129
max_value_asC=38000

def sensor_to_percentage(value, min_value, max_value):
    """Przekształca wartość sygnału czujnika na procenty."""
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
@@ -30,34 +28,38 @@ def sensor_to_percentage(value, min_value, max_value):
    percentage = (max_value - value) / (max_value - min_value) * 100
    return round(percentage, 2)

# Tworzenie magistrali SPI

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# Tworzenie układu MCP3008
# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D8)
print("cs D8: ", cs.value)
# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# Definiowanie kanałów
chan7 = AnalogIn(mcp, MCP.P7)  # Rezystancyjny
chan0 = AnalogIn(mcp, MCP.P0)  # Pojemnościowy
# configure GPIO7 as analog input via MCP3008
sensor = digitalio.DigitalInOut(board.D7)

chan7 = AnalogIn(mcp, MCP.P7)
chan0 = AnalogIn(mcp, MCP.P0)
while True:
    # create an analog input channel on pin: 0

    
    # Read analog voltage and raw value from GPIO7
    as0_voltage = chan0.voltage
    as0_raw = chan0.value
    as7_voltage = chan7.voltage
    as7_raw = chan7.value 
    print("")
    print("cd D7: ", sensor.value)
    print(f"Wartość rezystancyjna  {as7_raw} -> {sensor_to_percentage(as7_raw, min_value_asR, max_value_asR)}%")
    print(f"Wartość pojemnosciowa  {as0_raw} -> {sensor_to_percentage(as0_raw, min_value_asC, max_value_asC)}%")
    print("")
    print("")
    

    res_percent = sensor_to_percentage(as7_raw, min_value_asR, max_value_asR)
    cap_percent = sensor_to_percentage(as0_raw, min_value_asC, max_value_asC)

    print(f"Wartość rezystancyjna  {as7_raw} -> {res_percent}%")
    print(f"Wartość pojemnosciowa  {as0_raw} -> {cap_percent}%")

    # Wysyłanie danych do Blynk (TCP)
    blynk.virtual_write(PIN_RESISTANCE, res_percent)
    blynk.virtual_write(PIN_CAPACITANCE, cap_percent)
    time.sleep(3)

    # Obsługa zdarzeń Blynk (ważne, by Blynk działał poprawnie)
    blynk.run()

    time.sleep(3)
