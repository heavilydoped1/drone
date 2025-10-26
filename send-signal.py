from rtlsdr import RtlSdr
import numpy as np
import serial
import time
import random

NODE_ID = 2
SLOT_LENGTH = 0.5
CYCLE_LENGTH = 4 * SLOT_LENGTH
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

lora = None
sdr = None


def init_lora():
    global lora
    while True:
        try:
            lora = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
            print("LoRa bağlantısı kuruldu.")
            return
        except Exception as e:
            print(f"LoRa bağlanamadı: {e}, tekrar deneniyor...")
            time.sleep(2)


def init_sdr():
    global sdr
    while True:
        try:
            sdr = RtlSdr()
            sdr.sample_rate = 2.4e6
            sdr.center_freq = 446.450e6
            sdr.gain = 5
            print("SDR başlatıldı.")
            return
        except Exception as e:
            print(f"SDR başlatılamadı: {e}, tekrar deneniyor...")
            time.sleep(2)


print(f"drone{NODE_ID} başlatılıyor...")
init_lora()
init_sdr()

seq_id = 0
start_time = time.time()

while True:
    try:
        current_time = time.time()
        elapsed = (current_time - start_time) % CYCLE_LENGTH

        slot_start = (NODE_ID - 1) * SLOT_LENGTH
        slot_end = slot_start + SLOT_LENGTH

        if slot_start <= elapsed < slot_end:
            samples = sdr.read_samples(128*1024)  # biraz düşürdüm daha hızlı tepki için
            Psig = np.mean(np.abs(samples)**2)
            db = 10 * np.log10(Psig + 1e-12)  # log(0) koruması

            msg = f"{seq_id},drone{NODE_ID}:{db:.2f}\n"

            try:
                lora.write(msg.encode())
            except:
                print("LoRa yazma hatası. Yeniden bağlanılıyor...")
                init_lora()

            print(f"[drone{NODE_ID}] gönderildi: {msg.strip()}")
            seq_id += 1
            time.sleep(SLOT_LENGTH)

        else:
            time.sleep(0.05)

    except Exception as e:
        print(f"HATA OLDU: {e} | SDR yeniden başlatılıyor...")
        try:
            sdr.close()
        except:
            pass
        init_sdr()
