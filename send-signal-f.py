from rtlsdr import RtlSdr
import numpy as np
import serial
import time

# =====================
# TDMA AYARLARI
# =====================
NUM_DRONES = 4
SLOT_LENGTH = 2.5   # her drone için 0.5 saniye
CYCLE_LENGTH = NUM_DRONES * SLOT_LENGTH  # toplam döngü süresi

def init_lora():
    return serial.Serial('/dev/ttyUSB0', 9600)

def init_sdr():
    sdr = RtlSdr()
    sdr.sample_rate = 2.4e6
    sdr.center_freq = 446.450e6
    sdr.gain = 5
    return sdr

def send_to_lora(lora, drone_id, db):
    msg = f"drone {drone_id}: {db:.2f}"
    lora.write(msg.encode())
    print(f"GÖNDERİLDİ -> {msg}")

def get_signal_db(sdr):
    samples = sdr.read_samples(256*1024)
    Psig = np.mean(np.abs(samples)**2)
    Pfull = 1.0
    db = 10.0 * np.log10(Psig / Pfull)
    return db

try:
    lora = init_lora()
    sdr = init_sdr()
    print("Lora ve SDR başlatıldı!")

    start_time = time.time()

    while True:
        now = time.time() - start_time
        time_in_cycle = now % CYCLE_LENGTH

        # hangi drone'un sırası?
        drone_id = int(time_in_cycle // SLOT_LENGTH) + 1

        # o drone'un slot aralığı
        slot_start = (drone_id - 1) * SLOT_LENGTH
        slot_end = slot_start + SLOT_LENGTH

        # sadece kendi slotunda gönderim yapsın
        if slot_start <= time_in_cycle < slot_end:
            db = get_signal_db(sdr)
            send_to_lora(lora, drone_id, db)
            time.sleep(SLOT_LENGTH - 0.05)  # slot süresi kadar bekle
        else:
            time.sleep(0.01)

except KeyboardInterrupt:
    print("Simülasyon durduruldu.")

finally:
    try:
        sdr.close()
    except:
        pass
    print("SDR kapatıldı.")
