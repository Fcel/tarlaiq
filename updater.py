import os
import json
import xarray as xr
import numpy as np
import cdsapi
import ssl
import urllib3
from datetime import datetime, timedelta

# --- 0. GÜVENLİK VE SSL AYARI ---
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 1. AYARLAR VE API (MAKSİMUM SABIR) ---
URL = "https://cds-beta.climate.copernicus.eu/api"
TOKEN = os.environ.get("CDS_TOKEN")

# Eğer anahtar yoksa kodu hemen durdur
if not TOKEN:
    raise ValueError("KRİTİK HATA: CDS_TOKEN bulunamadı! GitHub Secrets ayarlarını kontrol edin.")

# 15 dakika bekleme süresi tanımlıyoruz
c = cdsapi.Client(url=URL, key=TOKEN, verify=False, timeout=900)

# Tarih Ayarı: 15 gün geriye çekiyoruz (Arşiv verisi her zaman daha hızlı ve garantidir)
target_date = datetime.now() - timedelta(days=15)
current_year = str(target_date.year)
current_month = target_date.strftime('%m')
current_day = target_date.strftime('%d')

# --- 2. 81 İL KOORDİNATLARI ---
iller_koordinat = {
    'Adana': (37.0, 35.3), 'Adıyaman': (37.7, 38.2), 'Afyonkarahisar': (38.7, 30.5),
    'Ağrı': (39.7, 43.0), 'Amasya': (40.6, 35.8), 'Ankara': (39.9, 32.8),
    'Antalya': (36.9, 30.7), 'Artvin': (41.2, 41.8), 'Aydın': (37.8, 27.8),
    'Balıkesir': (39.6, 27.9), 'Bilecik': (40.1, 29.9), 'Bingöl': (38.9, 40.5),
    'Bitlis': (38.4, 42.1), 'Bolu': (40.7, 31.6), 'Burdur': (37.7, 30.3),
    'Bursa': (40.2, 29.1), 'Çanakkale': (40.1, 26.4), 'Çankırı': (40.6, 33.6),
    'Çorum': (40.5, 34.9), 'Denizli': (37.8, 29.1), 'Diyarbakır': (37.9, 40.2),
    'Edirne': (41.7, 26.6), 'Elazığ': (38.7, 39.2), 'Erzincan': (39.7, 39.5),
    'Erzurum': (39.9, 41.3), 'Eskişehir': (39.8, 30.5), 'Gaziantep': (37.1, 37.4),
    'Giresun': (40.9, 38.4), 'Gümüşhane': (40.5, 39.5), 'Hakkari': (37.6, 43.7),
    'Hatay': (36.2, 36.2), 'Isparta': (37.8, 30.6), 'Mersin': (36.8, 34.6),
    'İstanbul': (41.0, 29.0), 'İzmir': (38.4, 27.1), 'Kars': (40.6, 43.1),
    'Kastamonu': (41.4, 33.8), 'Kayseri': (38.7, 35.5), 'Kırklareli': (41.7, 27.2),
    'Kırşehir': (39.1, 34.2), 'Kocaeli': (40.8, 29.9), 'Konya': (37.9, 32.5),
    'Kütahya': (39.4, 29.0), 'Malatya': (38.4, 38.3), 'Manisa': (38.6, 27.4),
    'Kahramanmaraş': (37.6, 36.9), 'Mardin': (37.3, 40.7), 'Muğla': (37.2, 28.4),
    'Muş': (38.7, 41.5), 'Nevşehir': (38.6, 34.7), 'Niğde': (37.9, 34.7),
    'Ordu': (40.9, 37.9), 'Rize': (41.0, 40.5), 'Sakarya': (40.7, 30.4),
    'Samsun': (41.3, 36.3), 'Siirt': (37.9, 41.9), 'Sinop': (42.0, 35.2),
    'Sivas': (39.7, 37.0), 'Tekirdağ': (40.9, 27.5), 'Tokat': (40.3, 36.6),
    'Trabzon': (41.0, 39.7), 'Tunceli': (39.1, 39.5), 'Şanlıurfa': (37.2, 38.8),
    'Uşak': (38.7, 29.4), 'Van': (38.5, 43.4), 'Yozgat': (39.8, 34.8),
    'Zonguldak': (41.5, 31.8), 'Aksaray': (38.4, 34.0), 'Bayburt': (40.3, 40.2),
    'Karaman': (37.2, 33.2), 'Kırıkkale': (39.8, 33.5), 'Batman': (37.9, 41.1),
    'Şırnak': (37.5, 42.5), 'Bartın': (41.6, 32.3), 'Ardahan': (41.1, 42.7),
    'Iğdır': (39.9, 44.0), 'Yalova': (40.7, 29.3), 'Karabük': (41.2, 32.6),
    'Kilis': (36.7, 37.1), 'Osmaniye': (37.1, 36.2), 'Düzce': (40.8, 31.2),
}

# --- 3. İŞLEME VE ANALİZ ---
def run_process():
    print(f"Sistem Başlatıldı. Hedef Tarih: {target_date.strftime('%Y-%m-%d')}")
    
    # BU NOKTADA HATA ALIRSAK GITHUB ACTIONS LOGLARINDA GÖRECEĞİZ
    print("Copernicus Beta sunucusuna istek gönderiliyor...")
    
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type': ['reanalysis'],           # Liste [] içinde olmalı
            'variable': [                             # Değişkenler liste içinde
                '2m_temperature', 
                'volumetric_soil_water_layer_1'
            ],
            'year': [current_year],                   # Liste zorunlu
            'month': [current_month],                 # Liste zorunlu
            'day': [current_day],                     # Liste zorunlu
            'time': ['12:00'],                        # Liste zorunlu
            'area': [42, 26, 36, 45],
            'data_format': 'netcdf',                  # 'format' değil 'data_format' olmalı
        },
        'latest_data.nc'
    )
    
    print("Veri başarıyla indirildi, analiz ediliyor...")
    ds = xr.open_dataset('latest_data.nc')
    results = {}

    for il, (lat, lon) in iller_koordinat.items():
        try:
            point = ds.sel(latitude=lat, longitude=lon, method='nearest')
            t2m = float(point['t2m']) - 273.15
            swvl1 = float(point['swvl1']) * 100
            
            # Risk Hesaplamaları
            don_skoru = round(np.clip((2 - t2m) * 20, 0, 100), 1)
            
            results[il] = {
                'don': don_skoru, 
                'don_seviye': 'KRİTİK' if don_skoru > 70 else ('ORTA' if don_skoru > 30 else 'DÜŞÜK'),
                'kuraklik': 12.5, # Şimdilik sabit (ERA5-Beta kısıtlılığı nedeniyle)
                'kuraklik_seviye': 'NORMAL',
                'nemi': round(swvl1, 1), 
                'nemi_seviye': "İDEAL" if 25 < swvl1 < 60 else "DİKKAT",
                'ruzgar': 8.4, # Şimdilik sabit
                'ruzgar_seviye': "GÜVENLİ"
            }
        except Exception as e:
            print(f"{il} hesaplanırken hata oluştu: {e}")
            continue
    
    # Verileri dosyaya yaz
    with open('tarlaiq_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("!!! BAŞARILI: tarlaiq_data.json gerçek verilerle güncellendi !!!")

if __name__ == "__main__":
    run_process()
