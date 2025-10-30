from rtlsdr import RtlSdr
import numpy as np
import serial
import serial.tools.list_ports
import time

NODE_ID = 2            
SLOT_DELAY = 2.5        
CYCLE_LENGTH = 10.0     
BAUD_RATE = 9600
lora = None
sdr = None

def find_lora():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "USB" in port.device:
            try:
                ser = serial.Serial(port.device, BAUD_RATE, timeout=0.3)
                time.sleep(0.1)
                ser.close()
                print(f"lora bulundu: {port.device}")
                return port.device
            except:
                pass
    return None
  
def init_lora():
    global lora
    while True:
        port = find_lora()
        if port:
            try:
                lora = serial.Serial(port, BAUD_RATE, timeout=0.1)
                print(f"lora baglandi: {port}")
                return
            except Exception as e:
                print(f"lora baglanamadi: {e}")
        print("lora bulunamadi, tekrar deneniyor...")
        time.sleep(2)
      
def init_sdr():
    global sdr
    while True:
        try:
            sdr = RtlSdr()
            sdr.sample_rate = 2.4e6
            sdr.center_freq = 446.450e6
            sdr.gain = 5
            print("sdr baslatildi.")
            return
        except Exception as e:
            print(f"sdr baslatilamadi: {e}")
            time.sleep(2)
          
print(f"drone{NODE_ID} başlatılıyor...")
init_lora()
init_sdr()
seq_id = 0
startup_delay = (NODE_ID - 1) * SLOT_DELAY
print(f"drone{NODE_ID} {startup_delay} saniye bekliyor...")
time.sleep(startup_delay)

while True:
    try:
        samples = sdr.read_samples(128 * 1024)
        Psig = np.mean(np.abs(samples)**2)
        db = 10 * np.log10(Psig + 1e-12)
        msg = f"{seq_id},drone{NODE_ID}:{db:.2f}\n"
        try:
            lora.write(msg.encode())
        except:
            print("lora yazma hatası yeniden bağlanıyor...")
            init_lora()
        print(f"[drone{NODE_ID}] gönderildi: {msg.strip()}")
        seq_id += 1
        time.sleep(CYCLE_LENGTH)
    except Exception as e:
        print(f"hata: {e} sdr yeniden başlatılıyor...")
        try:
            sdr.close()
        except:
            pass
        init_sdr()
