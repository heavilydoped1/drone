import subprocess
import time
import sys
import os

SCRIPT_PATH = "/home/pi/drone/drone_node.py"

while True:
    print("Watchdog: drone_node.py başlatılıyor...")
    try:
        process = subprocess.Popen(["python3", SCRIPT_PATH])
        process.wait()
        print("Watchdog: drone_node.py çöktü veya durdu!")
    except Exception as e:
        print(f"Watchdog hata: {e}")

    print("Watchdog: 3 saniye sonra tekrar denenecek...")
    time.sleep(3)
