from rtlsdr import RtlSdr
import numpy as np
import serial
import time

lora = serial.Serial('/dev/ttyUSB0', 9600)

def send_to_lora(power_db):
    lora.write(f"1. drone: {db:.2f}".encode())
    print(f"sended message from lora: {db:.2f}")

sdr = RtlSdr()
sdr.sample_rate = 2.4e6
sdr.center_freq = 446.450e6
sdr.gain = 5

try:
    while True:
        samples = sdr.read_samples(256*1024)
        Psig = np.mean(np.abs(samples)**2)
        Pfull = 1.0
        db = 10.0 * np.log10(Psig / Pfull)
        send_to_lora(db)
        time.sleep(0.01)

except KeyboardInterrupt:
    sdr.close()
    print("sdr closed")
