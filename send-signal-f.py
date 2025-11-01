from rtlsdr import RtlSdr
import numpy as np
import serial
import serial.tools.list_ports
import time

NUM_DRONES = 4
SLOT_LENGTH = 2.5
CYCLE_LENGTH = NUM_DRONES * SLOT_LENGTH
BAUD_RATE = 9600

def find_lora():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "USB" in port.device:
            try:
                ser = serial.Serial(port.device, BAUD_RATE, timeout=0.3)
                ser.close()
                print(f"LoRa bulundu: {port.device}")
                return port.device
            except:
                pass
    return None

def init_lora():
    while True:
        port = find_lora()
        if port:
            try:
                lora = serial.Serial(port, BAUD_RATE, timeout=0.1)
                print(f"LoRa bağlandı: {port}")
                return lora
            except Exception as e:
                print(f"LoRa bağlanamadı: {e}")
        print("LoRa bulunamadı, tekrar deneniyor...")
        time.sleep(2)

def init_sdr():
    while True:
        try:
            sdr = RtlSdr()
            sdr.sample_rate = 2.4e6
            sdr.center_freq = 446.450e6
            sdr.gain = 5
            print("SDR başlatıldı.")
            return sdr
        except Exception as e:
            print(f"SDR başlatılamadı: {e}")
            time.sleep(2)

def send_to_lora(lora, drone_id, db):
    msg = f"drone {drone_id}: {db:.2f}\n"
    try:
        lora.write(msg.encode())
        print(f"GÖNDERİLDİ -> {msg.strip()}")
    except Exception as e:
        print(f"LoRa hata: {e}. Yeniden bağlanıyor...")
        lora = init_lora()
    return lora

# Başlatma
print("TDMA Drone sistemi başlatılıyor...")
lora = init_lora()
sdr = init_sdr()

start_time = time.time()

while True:
    try:
        now = time.time() - start_time
        time_in_cycle = now % CYCLE_LENGTH
        drone_id = int(time_in_cycle // SLOT_LENGTH) + 1

        slot_start = (drone_id - 1) * SLOT_LENGTH
        slot_end = slot_start + SLOT_LENGTH

        if slot_start <= time_in_cycle < slot_end:
            samples = sdr.read_samples(128 * 1024)
            Psig = np.mean(np.abs(samples)**2)
            db = 10 * np.log10(Psig + 1e-12)
            lora = send_to_lora(lora, drone_id, db)
            time.sleep(SLOT_LENGTH - 0.05)
        else:
            time.sleep(0.05)

    except Exception as e:
        print(f"HATA: {e} | SDR yeniden başlatılıyor...")
        try:
            sdr.close()
        except:
            pass
        sdr = init_sdr()
