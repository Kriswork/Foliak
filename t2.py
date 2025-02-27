import BlynkLib
import time

BLYNK_AUTH_TOKEN = 'LLjO2Mzn4uNz99vFUsNe390yXd_-LMGK' # Upewnij się, że token jest poprawny.

try:
    blynk = BlynkLib.Blynk(BLYNK_AUTH_TOKEN, server="blynk.cloud", port=443)
    while True:
        blynk.run()
        time.sleep(0.1)
except Exception as e:
    print(f"Wystąpił błąd: {e}")
