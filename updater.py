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

# --- KONFİGÜRASYON ---
URL = "https://cds-beta.climate.copernicus.eu/api"
TOKEN = os.environ.get("CDS_TOKEN")

if not TOKEN:
    raise ValueError("HATA: CDS_TOKEN Eksik! GitHub Secrets ayarlarını kontrol edin.")

c = cdsapi.Client(url=URL, key=TOKEN, verify=False, timeout=1200)

# KRİTİK AYAR: 30 gün geriye gidiyoruz (Arşiv verisi 404 vermez)
target_date = datetime.now() - timedelta(days=30)
y, m, d = [str(target_date.year)], [target_date.strftime('%m')], [target_date.strftime('%d')]

# 81 İl Koordinat Listesi (Optimize Edilmiş)
iller_koordinat = {
    'Adana': (37.0, 35.3), 'Adıyaman': (37.7, 38.2), 'Afyonkarahisar': (38.7, 30.5), 'Ağrı': (39.7, 43.0),
    'Aksaray': (38.4, 34.0), 'Amasya': (40.6, 35.8), 'Ankara': (39.9, 32.8), 'Antalya': (36.9, 30.7),
    'Ardahan': (41.1, 42.7), 'Artvin': (41.2, 41.8), 'Aydın': (37.8, 27.8), 'Balıkesir': (39.6, 27.9),
    'Bartın': (41.6, 32.3), 'Batman': (37.9, 41.1), 'Bayburt': (40.3, 40.2), 'Bilecik': (40.1, 29.9),
    'Bingöl': (38.9, 40.5), 'Bitlis': (38.4, 42.1), 'Bolu': (40.7, 31.6), 'Burdur': (37.7, 30.3),
    'Bursa': (40.2, 29.1), 'Çanakkale': (40.1, 26.4), 'Çankırı': (40.6, 33.6), 'Çorum': (40.5, 34.9),
    'Denizli': (37.8, 29.1), 'Diyarbakır': (37.9, 40.2), 'Düzce': (40.8, 31.2), 'Edirne': (41.7, 26.6),
    'Elazığ': (38.7, 39.2), 'Erzincan': (39.7, 39.5), 'Erzurum': (39.9, 41.3), 'Eskişehir': (39.8, 30.5),
    'Gaziantep': (37.1, 37.4), 'Giresun': (40.9, 38.4), 'Gümüşhane': (40.5, 39.5), 'Hakkari': (37.6, 43.7),
    'Hatay': (36.2, 36.2), 'Iğdır': (39.9, 44.0), 'Isparta': (37.8, 30.6), 'İstanbul': (41.0, 29.0),
    'İzmir': (38.4, 27.1), 'Kahramanmaraş': (37.6, 36.9), 'Karabük': (41.2, 32.6), 'Karaman': (37.2, 33.2),
    'Kars': (40.6, 43.1), 'Kastamonu': (41.4, 33.8), 'Kayseri': (38.7, 35.5), 'Kırıkkale': (39.8, 33.5),
    'Kırklareli': (41.7, 27.2), 'Kırşehir': (39.1, 34.2), 'Kilis': (36.7, 37.1), 'Kocaeli': (40.8, 29.9),
    'Konya': (37.9, 32.5), 'Kütahya': (39.4, 29.0), 'Malatya': (38.4, 38.3), 'Manisa': (38.6, 27.4),
    'Mardin': (37.3, 40.7), 'Mersin': (36.8, 34.6), 'Muğla': (37.2, 28.4), 'Muş': (38.7, 41.5),
    'Nevşehir': (38.6, 34.7), 'Niğde': (37.9, 34.7), 'Ordu': (40.9, 37.9), 'Osmaniye': (37.1, 36.2),
    'Rize': (41.0, 40.5), 'Sakarya': (40.7, 30.4), 'Samsun': (41.3, 36.3), 'Siirt': (37.9, 41.9),
    'Sinop': (42.0, 35.2), 'Sivas': (39.7, 37.0), 'Şanlıurfa': (37.2, 38.8), 'Şırnak': (37.5, 42.5),
    'Tekirdağ': (40.9, 27.5), 'Tokat': (40.3, 36.6), 'Trabzon': (41.0, 39.7), 'Tunceli': (39.1, 39.5),
    'Uşak': (38.7, 29.4), 'Van': (38.5, 43.4), 'Yalova': (40.7, 29.3), 'Yozgat': (39.8, 34.8), 'Zonguldak': (41.5, 31.8)
}

def run_process():
    print(f"Sistem Başlatıldı. Hedef Tarih (30 Gün Önce): {target_date.strftime('%Y-%m-%d')}")
    
    try:
        # BETA SİSTEMİNE UYGUN LİSTE FORMATI
        c.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': ['reanalysis
