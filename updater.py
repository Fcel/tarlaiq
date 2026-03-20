import os
import json
import random
from datetime import datetime

def run():
    # GitHub'ın 'değişiklik yok' dememesi için her seferinde farklı bir sayı üretelim
    rastgele_sayi = round(random.uniform(10.0, 50.0), 2)
    su_an = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    data = {
        "Gümüşhane": {"don": rastgele_sayi, "nemi": rastgele_sayi, "durum": "SISTEM-AKTIF"},
        "Ankara": {"don": rastgele_sayi, "nemi": rastgele_sayi, "durum": "SISTEM-AKTIF"},
        "Son_Guncelleme": su_an
    }
    
    # Dosyayı fiziksel olarak diske yazıyoruz
    with open('tarlaiq_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"!!! BASARILI: Dosya {su_an} itibariyle yerelde olusturuldu (Deger: {rastgele_sayi}) !!!")

if __name__ == "__main__":
    run()
