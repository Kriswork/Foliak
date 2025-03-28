import digitalio
import board
import time
import busio
import BlynkLib  # Klient Blynk TCP
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from datetime import datetime

# KONFIGURACJA BLYNK
BLYNK_AUTH_TOKEN = 'LLjO2Mzn4uNz99vFUsNe390yXd_-LMGK'

def connect_blynk():
    """Tworzy nowe połączenie z Blynk."""
    return BlynkLib.Blynk(BLYNK_AUTH_TOKEN, server="fra1.blynk.cloud", port=443)

blynk = connect_blynk()

# Wirtualne piny w aplikacji Blynk
PIN_RESISTANCE = 0  # Odpowiada V0 w aplikacji Blynk
PIN_CAPACITANCE = 1  # Odpowiada V1
PIN_BUTTON = 2  # Odpowiada V2 (przycisk)
PIN_BUTTON_OUTPUT = 3  # Wirtualny pin do wysyłania wartości po naciśnięciu

# KONFIGURACJA CZUJNIKÓW
min_value_asR = 22000
max_value_asR = 65525
min_value_asC = 18129
max_value_asC = 35000

def sensor_to_percentage(value, min_value, max_value):
    """Przekształca wartość sygnału czujnika na procenty."""
    if value > max_value:
        return 0.0
    elif value < min_value:
        return 100.0
    
    percentage = (max_value - value) / (max_value - min_value) * 100
    return round(percentage, 2)

# Inicjalizacja SPI i MCP3008
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D8)
mcp = MCP.MCP3008(spi, cs)

chan7 = AnalogIn(mcp, MCP.P7)
chan0 = AnalogIn(mcp, MCP.P0)

# Funkcja wywoływana po naciśnięciu przycisku w Blynk
@blynk.on("V2")
def button_handler(value):
    if int(value[0]) == 1:  # Sprawdza, czy przycisk został naciśnięty
        res_percent = sensor_to_percentage(chan7.value, min_value_asR, max_value_asR)
        print(f"Przycisk naciśnięty! Wysyłam res_percent: {res_percent}%")
        blynk.virtual_write(PIN_BUTTON_OUTPUT, res_percent)
        
antysleep = 0

while True:
    try:
        if antysleep == 0:
            ap0_voltage = chan0.voltage
            ap0_raw = chan0.value
            ap7_voltage = chan7.voltage
            ap7_raw = chan7.value

            res_percent = sensor_to_percentage(ap7_raw, min_value_asR, max_value_asR)
            cap_percent = sensor_to_percentage(ap0_raw, min_value_asC, max_value_asC)

            # Wysyłanie danych do Blynk (TCP)
            blynk.virtual_write(PIN_RESISTANCE, res_percent)
            blynk.virtual_write(PIN_CAPACITANCE, cap_percent)
            print(f"Wysyłam res_percent: {res_percent}%, {cap_percent}%")
        antysleep = antysleep + 1

        if antysleep == 100:
            antysleep = 0
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M")
            print("reset", date_str, time_str)

        
        # Obsługa zdarzeń Blynk
        blynk.run()
    
    except Exception as e:
        print(f"Błąd połączenia z Blynk: {e}. Ponowna próba za 5 sekund...")
        print("Brak połaczenia")
        time.sleep(5)
        blynk = connect_blynk()

    time.sleep(20)
