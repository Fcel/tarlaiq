import os
import json
import pandas as pd
import xarray as xr
import numpy as np
import cdsapi
from datetime import datetime

# --- 1. AYARLAR VE API BAĞLANTISI ---
# GitHub Secrets'tan gelecek olan Token
URL = "https://cds-beta.climate.copernicus.eu/api"
TOKEN = os.environ.get("CDS_TOKEN") 

if not TOKEN:
    raise ValueError("CDS_TOKEN bulunamadı! GitHub Secrets ayarlarını kontrol edin.")

c = cdsapi.Client(url=URL, key=TOKEN)

# Dinamik Tarih Ayarı (Şu anki ayı ve yılı al)
current_year = str(datetime.now().year)
current_month = datetime.now().strftime('%m')
# Günlük veri (ERA5 gecikmeli gelir, düne kadar olan günleri alıyoruz)
day_limit = datetime.now().day if datetime.now().day > 1 else 2
current_days = [f"{i:02d}" for i in range(1, day_limit)]

# --- 2. 81 İL KOORDİNAT VERİTABANI ---
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

# --- 3. VERİ ÇEKME (RETRIEVE) ---
def fetch_data():
    print(f"Veriler indiriliyor... (Yıl: {current_year}, Ay: {current_month})")
    
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type': 'reanalysis',
            'variable': [
                '2m_temperature', 
                'total_precipitation', 
                'potential_evaporation'
            ],
            'year': [current_year],
            'month': [current_month],
            'day': current_days,
            'time': ['00:00', '06:00', '12:00', '18:00'],
            'area': [42, 26, 36, 45], # Kuzey, Batı, Güney, Doğu
            'format': 'netcdf',
        },
        'latest_data.nc'
    )
    return xr.open_dataset('latest_data.nc')

# --- 4. RİSK HESAPLAMA ---
def calculate_risks(ds):
    print("Risk skorları hesaplanıyor...")
    
    # Don Skoru (Kelvin -> Celsius)
    temp = ds['t2m'] - 273.15
    # Minimum sıcaklığa göre 0-100 arası skor
    min_temp = temp.min(dim='time')
    don_map = np.clip((2 - min_temp) * 20, 0, 100)
    
    # Kuraklık Skoru
    yagis = ds['tp'] * 1000
    pet = abs(ds['pev']) * 1000
    # Yağış / Buharlaşma oranı
    oran = yagis.mean(dim='time') / (pet.mean(dim='time') + 0.001)
    kuraklik_map = np.clip((1 - oran) * 50, 0, 100)
    
    # Yağış Skoru
    yagis_map = np.clip(yagis.mean(dim='time') * 7 * 2, 0, 100)
    
    return don_map, kuraklik_map, yagis_map

# --- 5. JSON ÇIKTISI OLUŞTURMA ---
def create_json(don_map, kuraklik_map, yagis_map):
    results = {}
    
    def get_level(skor):
        if skor >= 70: return 'KRİTİK'
        elif skor >= 40: return 'YÜKSEK'
        elif skor >= 20: return 'ORTA'
        else: return 'DÜŞÜK'

    for il, (lat, lon) in iller_koordinat.items():
        try:
            d_val = float(don_map.sel(latitude=lat, longitude=lon, method='nearest'))
            k_val = float(kuraklik_map.sel(latitude=lat, longitude=lon, method='nearest'))
            y_val = float(yagis_map.sel(latitude=lat, longitude=lon, method='nearest'))
            
            results[il] = {
                'don': round(d_val, 1),
                'don_seviye': get_level(d_val),
                'kuraklik': round(k_val, 1),
                'kuraklik_seviye': get_level(k_val),
                'yagis': round(y_val, 1),
                'yagis_seviye': get_level(y_val)
            }
        except Exception as e:
            print(f"{il} için veri çekilemedi: {e}")
    
    with open('tarlaiq_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("tarlaiq_data.json başarıyla güncellendi!")

# --- ANA ÇALIŞTIRICI ---
if __name__ == "__main__":
    try:
        ds = fetch_data()
        don, kurak, yagis = calculate_risks(ds)
        create_json(don, kurak, yagis)
    except Exception as e:
        print(f"Hata oluştu: {e}")
