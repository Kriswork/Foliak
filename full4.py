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
dht_device = adafruit_dht.DHT22(board.D7)  # GPIO7

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
        file.write("Data\tGodzina\tNapięcie(V)_C_(P0)\tRAW_C_(P0)\tProcent_C_(P0)\t"
                   "Napięcie(V)_R_(P7)\tRAW_R_(P7)\tProcent_R_(P7)\tTemperatura(C)\tWilgotność(%)\n")
except FileExistsError:
    pass

time.sleep(1)

while True:
    # Odczyt danych z MCP3008
    chan7 = AnalogIn(mcp, MCP.P7)
    chan0 = AnalogIn(mcp, MCP.P0)
    
    ap0_voltage = chan0.voltage
    ap0_raw = chan0.value
    ap7_voltage = chan7.voltage
    ap7_raw = chan7.value
    
    # Odczyt z DHT22
    temperature = dht_device.temperature
    humidity = dht_device.humidity
    #humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    
    if humidity is None or temperature is None:
        humidity = "Błąd"
        temperature = "Błąd"
    else:
        humidity = round(humidity, 2)
        temperature = round(temperature, 2)
    print("Temperatura: {temperature}, Wilgotność powietrze: {humidity}")
    # Pobranie aktualnej daty i godziny
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    
    # Formatowanie danych do logowania
    log_entry = (f"{date_str}\t{time_str}\t{ap0_voltage:.2f}\t{ap0_raw}\t{sensor_to_percentage(ap0_raw, min_value_asC, max_value_asC)}%\t"
                 f"{ap7_voltage:.2f}\t{ap7_raw}\t{sensor_to_percentage(ap7_raw, min_value_asR, max_value_asR)}%\t"
                 f"{temperature}\t{humidity}\n")
    
    # Zapis do pliku
    with open(file_path, "a") as file:
        file.write(log_entry)
    
    # print(log_entry.strip())
    time.sleep(1800)
