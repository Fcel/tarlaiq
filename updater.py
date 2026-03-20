import os
import json
import xarray as xr
import numpy as np
import cdsapi
import ssl
import urllib3
from datetime import datetime, timedelta

# --- GÜVENLİK ---
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- AYARLAR ---
URL = "https://cds-beta.climate.copernicus.eu/api"
TOKEN = os.environ.get("CDS_TOKEN")

if not TOKEN:
    raise ValueError("HATA: CDS_TOKEN Eksik! GitHub Secrets ayarını kontrol et.")

c = cdsapi.Client(url=URL, key=TOKEN, verify=False, timeout=600)

# Veri garantisi için 20 gün geriye gidiyoruz
target_date = datetime.now() - timedelta(days=20)
y, m, d = [str(target_date.year)], [target_date.strftime('%m')], [target_date.strftime('%d')]

iller = {'Gümüşhane': (40.5, 39.5), 'Ankara': (39.9, 32.8), 'İstanbul': (41.0, 29.0)}

def run():
    print(f"İşlem Başladı: {target_date.strftime('%Y-%m-%d')}")
    
    # EĞER BURADA HATA VARSA ROBOT KIRMIZI YANACAK (404, Kütüphane vb.)
    c.retrieve('reanalysis-era5-single-levels', {
        'product_type': ['reanalysis'],
        'variable': ['2m_temperature', 'volumetric_soil_water_layer_1'],
        'year': y, 'month': m, 'day': d, 'time': ['12:00'],
        'area': [42, 26, 36, 45], 'data_format': 'netcdf',
    }, 'latest_data.nc')
    
    ds = xr.open_dataset('latest_data.nc')
    results = {}

    for il, (lat, lon) in iller.items():
        pt = ds.sel(latitude=lat, longitude=lon, method='nearest')
        temp = float(pt['t2m']) - 273.15
        soil = float(pt['swvl1']) * 100
        
        results[il] = {
            'don': round(temp, 1), 
            'don_seviye': 'TEST-AKTIF',
            'kuraklik': 15.0, 
            'nemi': round(soil, 1), 
            'ruzgar': 10.0,
            'zaman': datetime.now().strftime('%H:%M:%S')
        }
    
    with open('tarlaiq_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("!!! BAŞARILI: DOSYA YAZILDI !!!")

if __name__ == "__main__":
    run()
