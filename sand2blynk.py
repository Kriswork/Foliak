import digitalio
import board
import time
import busio
import BlynkLib  # Klient Blynk TCP
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# KONFIGURACJA BLYNK
BLYNK_AUTH_TOKEN = 'Zxw6Dh-9z609JoYpgecxqh6BvV7_blJ7'
blynk = BlynkLib.Blynk(BLYNK_AUTH_TOKEN, server="fra1.blynk.cloud", port=80)

# Wirtualne piny w aplikacji Blynk
PIN_RESISTANCE = 0  # Odpowiada V0 w aplikacji Blynk
PIN_CAPACITANCE = 1  # Odpowiada V1
PIN_AP0_VOLTAGE_BUTTON = 2  # Odpowiada V2 (nowy pin do odczytu ap0_voltage)

# KONFIGURACJA CZUJNIKÓW
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

chan7 = AnalogIn(mcp, MCP.P7)
chan0 = AnalogIn(mcp, MCP.P0)

def send_ap0_voltage():
    """Wysyła wartość napięcia z kanału 0 do Blynk po naciśnięciu przycisku."""
    ap0_voltage = chan0.voltage
    print(f"Przycisk naciśnięty! Wysyłam ap0_voltage: {ap0_voltage} V")
    blynk.virtual_write(PIN_AP0_VOLTAGE_BUTTON, ap0_voltage)

# Obsługa przycisku w aplikacji Blynk
def v2_write_handler(pin, value):
    if int(value[0]) == 1:  # Jeśli przycisk został naciśnięty (wartość 1)
        send_ap0_voltage()

# Rejestracja handlera dla przycisku na V2
blynk.add_virtual_pin(PIN_AP0_VOLTAGE_BUTTON, write=v2_write_handler)

while True:

    ap0_voltage = chan0.voltage # wartość w Voltach pin analgowy 0 (MCP3008)
    ap0_raw = chan0.value  # wartość raw pin analgowy 0 (MCP3008)
    ap7_voltage = chan7.voltage # wartość w Voltach pin analgowy 7 (MCP3008)
    ap7_raw = chan7.value # wartość raw pin analgowy 7 (MCP3008)
    

    res_percent = sensor_to_percentage(ap7_raw, min_value_asR, max_value_asR)
    cap_percent = sensor_to_percentage(ap0_raw, min_value_asC, max_value_asC)

    # Wysyłanie danych do Blynk (TCP)
    blynk.virtual_write(PIN_RESISTANCE, res_percent)
    blynk.virtual_write(PIN_CAPACITANCE, cap_percent)

    # Obsługa zdarzeń Blynk (ważne, by Blynk działał poprawnie)
    blynk.run()

    time.sleep(3600)
