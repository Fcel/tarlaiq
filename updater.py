import os
import json
import random
from datetime import datetime

# --- AYARLAR ---
# Şimdilik Copernicus'u devreden çıkarıp sadece yazma yetkisini test ediyoruz
TOKEN = os.environ.get("CDS_TOKEN")

def run():
    print(f"Sistem Başlatıldı. Zaman: {datetime.now()}")
    
    # GitHub'ın 'now' yazması için KESİN DEĞİŞİKLİK ŞART
    # Her çalıştığında farklı bir sayı üretir ki Git 'değişiklik yok' diyemesin
    random_val = round(random.uniform(10.0, 50.0), 2)
    
    data = {
        "Gümüşhane": {"don": random_val, "nemi": random_val, "durum": "TEST-OK"},
        "Ankara": {"don": random_val, "nemi": random_val, "durum": "TEST-OK"},
        "Sistem_Zamani": str(datetime.now())
    }
    
    # Dosyayı yaz
    with open('tarlaiq_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"!!! BAŞARILI: DOSYA YERELDE OLUŞTURULDU (Deger: {random_val}) !!!")

if __name__ == "__main__":
    run()
