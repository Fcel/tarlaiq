import os
import json
import xarray as xr
import numpy as np
import cdsapi
import ssl
import urllib3
from datetime import datetime, timedelta

# --- GÜVENLİK AYARLARI ---
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- KONFİGÜRASYON ---
URL = "https://cds-beta.climate.copernicus.eu/api"
TOKEN = os.environ.get("CDS_TOKEN")

# Eğer anahtar yoksa sistemi hemen durdur
if not TOKEN:
    raise ValueError("HATA: CDS_TOKEN bulunamadı! GitHub Secrets ayarlarını kontrol edin.")

c = cdsapi.Client(url=URL, key=TOKEN, verify=False, timeout=1200)

# Veri garantisi için 20 gün geriye gidiyoruz
target_date = datetime.now() - timedelta(days=20)
current_year = [str(target_date.year)]
current_month = [target_date.strftime('%m')]
current_day = [target_date.strftime('%d')]

# Test ve ana iller listesi
iller_koordinat = {
    'Adana': (37.0, 35.3), 'Ankara': (39.9, 32.8), 'Gümüşhane': (40.5, 39.5),
    'İstanbul': (41.0, 29.0), 'İzmir': (38.4, 27.1), 'Antalya': (36.9, 30.7)
}

def run_process():
    print(f"Sistem Başlatıldı. Hedef Tarih: {target_date.strftime('%Y-%m-%d')}")
    
    # 404 VEYA 500 HATASI ALIRSA BURADA ROBOT DURACAK VE BİZE SEBEBİNİ SÖYLEYECEK
    print("Copernicus Beta sunucusuna istek gönderiliyor...")
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type': ['reanalysis'],
            'variable': [
                '2m_temperature', 
                'volumetric_soil_water_layer_1'
            ],
            'year': current_year,
            'month': current_month,
            'day': current_day,
            'time': ['12:00'], 
            'area': [42, 26, 36, 45], # Türkiye
            'data_format': 'netcdf',
        },
        'latest_data.nc'
    )
    
    print("Veri indirildi, işleniyor...")
    ds = xr.open_dataset('latest_data.nc')
    results = {}

    for il, (lat, lon) in iller_koordinat.items():
        try:
            pt = ds.sel(latitude=lat, longitude=lon, method='nearest')
            t2m = float(pt['t2m']) - 273.15
            swvl1 = float(pt['swvl1']) * 100
            
            results[il] = {
                'don': round(t2m, 1), 
                'don_seviye': 'TEST-AKTIF',
                'kuraklik': 12.0, 
                'kuraklik_seviye': 'NORMAL',
                'nemi': round(swvl1, 1), 
                'nemi_seviye': "İDEAL" if 20 < swvl1 < 60 else "DİKKAT",
                'ruzgar': 8.0, 
                'ruzgar_seviye': "GÜVENLİ"
            }
        except Exception as e:
            print(f"{il} için veri işlenemedi: {e}")
    
    # Dosyayı yaz
    with open('tarlaiq_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("!!! BAŞARILI: tarlaiq_data.json dosyası güncellendi !!!")

if __name__ == "__main__":
    run_process()
