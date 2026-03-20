import os
import json
import xarray as xr
import numpy as np
import cdsapi
import ssl
import urllib3
from datetime import datetime, timedelta

# --- GÜVENLİK VE SSL ---
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- AYARLAR ---
URL = "https://cds-beta.climate.copernicus.eu/api"
TOKEN = os.environ.get("CDS_TOKEN")
# Timeout süresini 20 dakikaya çıkardık (Kuyruk beklemek için)
c = cdsapi.Client(url=URL, key=TOKEN, verify=False, timeout=1200)

# Tarih: 15 gün geriye çekiyoruz (Arşiv verisi daha hızlı gelir)
target_date = datetime.now() - timedelta(days=15)
current_year = [str(target_date.year)]
current_month = [target_date.strftime('%m')]
current_day = [target_date.strftime('%d')]

iller_koordinat = {
    'Adana': (37.0, 35.3), 'Ankara': (39.9, 32.8), 'Gümüşhane': (40.5, 39.5),
    'İstanbul': (41.0, 29.0), 'İzmir': (38.4, 27.1), 'Antalya': (36.9, 30.7)
}

def run_process():
    print(f"İşlem Başladı. Hedef Tarih: {target_date.strftime('%Y-%m-%d')}")
    try:
        # BETA SİSTEMİ İÇİN KRİTİK LİSTE FORMATI
        c.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': ['reanalysis'],
                'variable': [
                    '2m_temperature', 
                    'volumetric_soil_water_layer_1',
                    '10m_wind_speed',
                    'total_precipitation'
                ],
                'year': current_year,
                'month': current_month,
                'day': current_day,
                'time': ['12:00'],
                'area': [42.1, 26.0, 35.9, 44.9],
                'data_format': 'netcdf', # 'format' değil 'data_format'
            },
            'latest_data.nc'
        )
        
        ds = xr.open_dataset('latest_data.nc')
        results = {}

        for il, (lat, lon) in iller_koordinat.items():
            pt = ds.sel(latitude=lat, longitude=lon, method='nearest')
            temp = float(pt['t2m']) - 273.15
            soil = float(pt['swvl1']) * 100
            wind = float(pt['si10']) * 3.6
            rain = float(pt['tp']) * 1000
            
            don = round(np.clip((2 - temp) * 15, 0, 100), 1)
            results[il] = {
                'don': don, 
                'don_seviye': 'KRİTİK' if don > 70 else 'DÜŞÜK',
                'kuraklik': round(np.clip(50 - (rain * 10), 0, 100), 1),
                'kuraklik_seviye': 'NORMAL',
                'nemi': round(soil, 1), 
                'nemi_seviye': "İDEAL" if 25 < soil < 60 else "DİKKAT",
                'ruzgar': round(wind, 1),
                'ruzgar_seviye': "GÜVENLİ"
            }
        
        with open('tarlaiq_data.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("BAŞARILI: Veriler güncellendi.")

    except Exception as e:
        print(f"HATA: {e}")

if __name__ == "__main__":
    run_process()
