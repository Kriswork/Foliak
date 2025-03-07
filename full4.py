import busio
import digitalio
import board
import time
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from datetime import datetime
import adafruit_dht  # Biblioteka do obsługi DHT22

# Ustawienia dla czujnika DHT22
# DHT_SENSOR = Adafruit_DHT.DHT22
# DHT_PIN = 4  # GPIO4 (Dostosuj do swojego podłączenia)
dht_device = adafruit_dht.DHT22(board.D4)  # GPIO7

min_value_asR = 22000
max_value_asR = 65525
min_value_asC = 18129
max_value_asC = 38000

def sensor_to_percentage(value, min_value, max_value):
    """
    Przekształca wartość sygnału czujnika na procenty.
    """
    if value > max_value:
        return 0.0
    elif value < min_value:
        return 100.0
    
    percentage = (max_value - value) / (max_value - min_value) * 100
    return round(percentage, 2)

# Tworzenie interfejsu SPI
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D8)
mcp = MCP.MCP3008(spi, cs)

# Plik do przechowywania danych
file_path = "nawodnienie_zapis.txt"

# Tworzenie pliku, jeśli nie istnieje
try:
    with open(file_path, "x") as file:
        file.write("Data\tGodzina\tNapięcie(V)_C_(P0)\tRAW_C_(P0)\tProcent_C_(P0)\tNapięcie(V)_R_(P7)\tRAW_R_(P7)\tProcent_R_(P7)\t"
                   "Napięcie(V)_C_(P1)\tRAW_C_(P1)\tProcent_C_(P1)\tTemperatura(C)\tWilgotność(%)\tLux raw\tLux V\n")
except FileExistsError:
    pass

while True:
    # Odczyt danych z MCP3008
    chan7 = AnalogIn(mcp, MCP.P7) # sensor czujnik wilgotności gleby rezystancyjny
    chan0 = AnalogIn(mcp, MCP.P0) # sensor czujnik wilgotności gleby pojemnościowy 1.2
    chan1 = AnalogIn(mcp, MCP.P1) # sensor czujnik wilgotności gleby pojemnościowy 2.0
    chan4 = AnalogIn(mcp, MCP.P4) # fotorezystor
    
    as0_voltage = chan0.voltage
    as0_raw = chan0.value
    as1_voltage = chan1.voltage
    as1_raw = chan1.value
    as7_voltage = chan7.voltage
    as7_raw = chan7.value 
    
    # Odczyt z DHT22
    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
    except RuntimeError as error:
        print(f"Błąd odczytu DHT22: {error}")
        temperature = None
        humidity = None

    # Pobranie aktualnej daty i godziny
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    
    # Formatowanie danych do logowania
    log_entry = (f"{date_str}\t{time_str}\t{ap0_voltage:.2f}\t{ap0_raw}\t{sensor_to_percentage(ap0_raw, min_value_asC, max_value_asC)}%\t"
                 f"{ap7_voltage:.2f}\t{ap7_raw}\t{sensor_to_percentage(ap7_raw, min_value_asR, max_value_asR)}%\t"
                 f"{ap1_voltage:.2f}\t{ap1_raw}\t{sensor_to_percentage(ap1_raw, min_value_asR, max_value_asR)}%\t"
                 f"{temperature}\t{humidity}\t{chan4.value}\t{chan4.voltage}\n")
    
    # Zapis do pliku
    with open(file_path, "a") as file:
        file.write(log_entry)
    
    print(log_entry.strip())
    time.sleep(1800)
