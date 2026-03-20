# --- updater.py İÇİNDEKİ DEĞİŞİKLİKLER ---

# 1. Veri İsteme Kısmı (Variable listesine ekleme yapıyoruz)
c.retrieve(
    'reanalysis-era5-single-levels',
    {
        'product_type': 'reanalysis',
        'variable': [
            '2m_temperature', 
            'total_precipitation', 
            'potential_evaporation',
            'volumetric_soil_water_layer_1', # Toprak Nemi (0-7cm)
            '10m_wind_speed' # Rüzgar Hızı
        ],
        # ... diğer tarih ve area ayarları aynı kalıyor ...
    },
    'latest_data.nc'
)

# 2. Risk Hesaplama Kısmı (Yeni fonksiyonlar)
def calculate_risks(ds):
    # ... eski hesaplamalar (don, kuraklik) burada duruyor ...
    
    # Toprak Nemi Skoru (0-1 arası değeri 0-100'e çeviriyoruz)
    # Genelde 0.2 altı çok kuru, 0.4 üstü doygundur.
    nemi = ds['swvl1'].mean(dim='time')
    nemi_map = np.clip(nemi * 200, 0, 100) # Basit bir ölçeklendirme
    
    # Rüzgar Riski (m/s cinsinden)
    # 8 m/s üstü ilaçlama için risklidir, 15 m/s fırtına riskidir.
    ruzgar = ds['si10'].max(dim='time')
    ruzgar_map = np.clip(ruzgar * 5, 0, 100) # 20 m/s hızı %100 risk yapar
    
    return don_map, kuraklik_map, yagis_map, nemi_map, ruzgar_map
