import streamlit as st
import pandas as pd
import json
import os
import cdsapi

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="TarlaIQ | Dr. Fatih",
    page_icon="🌱",
    layout="wide"
)

# --- GÜVENLİK: YENİ CDS BETA TOKEN KULLANIMI ---
# Streamlit Secrets panelinden CDS_TOKEN adıyla okunur
try:
    if "CDS_TOKEN" in st.secrets:
        TOKEN = st.secrets["CDS_TOKEN"]
        # Yeni Beta URL'si
        URL = "https://cds-beta.climate.copernicus.eu/api"
        # Client kurulumu (İleride otomatik güncelleme yaparsan lazım olacak)
        c = cdsapi.Client(url=URL, key=TOKEN)
    else:
        st.sidebar.warning("⚠️ CDS_TOKEN Secrets panelinde bulunamadı.")
except Exception as e:
    st.sidebar.error(f"Bağlantı Ayarı Hatası: {e}")

# --- VERİ YÜKLEME ---
@st.cache_data
def load_tarlaiq_data():
    # GitHub'daki json dosyasını okur
    if os.path.exists('tarlaiq_data.json'):
        with open('tarlaiq_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

data = load_tarlaiq_data()

# --- ARAYÜZ TASARIMI ---
st.title("🌱 TarlaIQ: Akıllı Tarımsal Risk Platformu")
st.markdown("### Veriye Dayalı Karar Destek Sistemi")

if data:
    iller = sorted(list(data.keys()))
    
    # Üst Bölüm: Seçim ve Ana Skorlar
    col_secim, col_don, col_kurak, col_yagis = st.columns([1.5, 1, 1, 1])
    
    with col_secim:
        st.info("📍 Analiz edilecek ili seçin:")
        secilen_il = st.selectbox("", iller, index=iller.index("Gümüşhane") if "Gümüşhane" in iller else 0)
    
    v = data[secilen_il]
    
    with col_don:
        st.metric("Don Riski", f"%{v['don']}", v['don_seviye'], delta_color="inverse")
    
    with col_kurak:
        st.metric("Kuraklık Skoru", f"%{v['kuraklik']}", v['kuraklik_seviye'], delta_color="inverse")
        
    with col_yagis:
        st.metric("Yağış Skoru", v['yagis'], v['yagis_seviye'])

    st.divider()

    # --- DETAYLI TABLO VE ANALİZ ---
    tab1, tab2 = st.tabs(["📊 Risk Sıralaması", "ℹ️ Proje Hakkında"])
    
    with tab1:
        st.subheader("81 İl Risk Veritabanı")
        df = pd.DataFrame.from_dict(data, orient='index').reset_index()
        df.columns = ['İl', 'Don Skoru', 'Don Seviyesi', 'Kuraklık Skoru', 'Kuraklık Seviyesi', 'Yağış Skoru', 'Yağış Seviyesi']
        
        # Filtreleme veya Sıralama
        st.dataframe(df.sort_values('Don Skoru', ascending=False), use_container_width=True, hide_index=True)

    with tab2:
        st.write(f"""
        **TarlaIQ**, Dr. Fatih tarafından geliştirilen bir tarımsal izleme platformudur.
        - **Veri Kaynağı:** Copernicus ERA5 Reanalysis (Yüksek Çözünürlüklü Atmosfer Verileri)
        - **Kapsam:** Türkiye geneli 81 ilin iklimsel risk analizi.
        - **Teknoloji:** Python, Streamlit ve CDS API (Modernised Beta).
        """)

else:
    st.error("❌ Veri dosyası (tarlaiq_data.json) bulunamadı! Lütfen dosyayı GitHub'a yükleyin.")

# --- YAN MENÜ ---
st.sidebar.image("https://www.tubitak.gov.tr/sites/default/files/logo_tubitak.png", width=100) # Örnek logo
st.sidebar.markdown(f"## 🛠️ Panel")
st.sidebar.write(f"**Aktif İl:** {secilen_il if data else 'Seçilmedi'}")
st.sidebar.write("---")
st.sidebar.write("👨‍🔬 **Dr. Fatih CELIK**")
st.sidebar.caption("Tarımsal veri bilimi ve yapay zeka çözümleri.")
