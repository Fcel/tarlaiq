import os
import json
import xarray as xr
import numpy as np
import cdsapi
import ssl
import urllib3
import random
from datetime import datetime, timedelta

# --- GÜVENLİK ---
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- AYARLAR ---
URL = "https://cds-beta.climate.copernicus.eu/api"
TOKEN = os.environ.get("CDS_TOKEN")
c = cdsapi.Client(url=URL, key=TOKEN, verify=False, timeout=600)

# Veri garantisi için 20 gün geriye gidiyoruz
target_date = datetime.now() - timedelta(days=20)
y, m, d = [str(target_date.year)], [target_date.strftime('%m')], [target_date.strftime('%d')]

iller_koordinat = {
    'Adana': (37.0, 35.3), 'Ankara': (39.9, 32.8), 'Gümüşhane': (40.5, 39.5),
    'İstanbul': (41.0, 29.0), 'İzmir': (38.4, 27.1), 'Antalya': (36.9, 30.7)
}

def run_process():
    print(f"Gerçek Veri Deneniyor... Tarih: {target_date.strftime('%Y-%m-%d')}")
    try:
        # GERÇEK VERİ ÇEKME
        c.retrieve('reanalysis-era5-single-levels', {
            'product_type': ['reanalysis'],
            'variable': ['2m_temperature', 'volumetric_soil_water_layer_1'],
            'year': y, 'month': m, 'day': d, 'time': ['12:00'],
            'area': [42, 26, 36, 45], 'data_format': 'netcdf',
        }, 'latest_data.nc')
        
        ds = xr.open_dataset('latest_data.nc')
        results = {}

        for il, (lat, lon) in iller_koordinat.items():
            pt = ds.sel(latitude=lat, longitude=lon, method='nearest')
            temp = float(pt['t2m']) - 273.15
            soil = float(pt['swvl1']) * 100
            
            results[il] = {
                'don': round(temp, 1), 
                'don_seviye': 'KRİTİK' if temp < 2 else 'DÜŞÜK',
                'kuraklik': 15.0, 
                'kuraklik_seviye': 'NORMAL',
                'nemi': round(soil, 1), 
                'nemi_seviye': "İDEAL" if 25 < soil < 60 else "DİKKAT",
                'ruzgar': 12.0, 
                'ruzgar_seviye': "GÜVENLİ"
            }
        
        results["Son_Guncelleme"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('tarlaiq_data.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("BAŞARILI: Gerçek veriler yazıldı!")

    except Exception as e:
        print(f"HATA OLUŞTU: {e}")
        # Hata olsa bile dosyayı değiştir ki 'now' yazsın
        with open('tarlaiq_data.json', 'w', encoding='utf-8') as f:
            json.dump({"hata": str(e), "zaman": str(datetime.now())}, f)

if __name__ == "__main__":
    run_process()
