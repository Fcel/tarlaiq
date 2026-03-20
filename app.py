import streamlit as st
import pandas as pd
import json
import os

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="TarlaIQ | Dr. Fatih",
    page_icon="🌱",
    layout="wide"
)

# --- GÜVENLİK: API BİLGİLERİNİ ÇEKME ---
# Bu bilgiler Streamlit Panelindeki "Secrets" kısmından gelecek
try:
    CDS_UID = st.secrets["CDS_UID"]
    CDS_API_KEY = st.secrets["CDS_API_KEY"]
except:
    st.warning("⚠️ API Anahtarları (Secrets) henüz tanımlanmamış. Yerel veriler kullanılıyor.")

# --- VERİ YÜKLEME FONKSİYONU ---
@st.cache_data
def load_tarlaiq_data():
    # Colab'da oluşturup GitHub'a yüklediğin JSON dosyasını okur
    if os.path.exists('tarlaiq_data.json'):
        with open('tarlaiq_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return None

# Veriyi çek
data = load_tarlaiq_data()

# --- ARAYÜZ TASARIMI ---
st.title("🌱 TarlaIQ: Akıllı Tarımsal Risk Platformu")
st.markdown(f"**Geliştirici:** Dr. Fatih | **Veri Kaynağı:** Copernicus ERA5")

if data:
    # İl listesini hazırla
    iller = sorted(list(data.keys()))
    
    # Üst Bilgi Kartları için kolonlar
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        secilen_il = st.selectbox("📍 Analiz edilecek ili seçin:", iller, index=iller.index("Gümüşhane") if "Gümüşhane" in iller else 0)
    
    v = data[secilen_il]
    
    with col2:
        st.metric("Don Riski", f"%{v['don']}", v['don_seviye'], delta_color="inverse")
    
    with col3:
        st.metric("Kuraklık Skoru", f"%{v['kuraklik']}", v['kuraklik_seviye'], delta_color="inverse")
        
    with col4:
        st.metric("Yağış Skoru", v['yagis'], v['yagis_seviye'])

    st.divider()

    # --- ANA İÇERİK ---
    tab1, tab2 = st.tabs(["📊 Risk Detayları", "🗺️ Bölgesel Analiz"])
    
    with tab1:
        st.subheader(f"{secilen_il} İli İçin Detaylı Analiz")
        st.write(f"Bu sonuçlar Ocak-Mart 2023/2024 döneminin ortalama atmosferik verilerine dayanmaktadır.")
        
        # Tüm illeri tablo olarak göster
        df = pd.DataFrame.from_dict(data, orient='index').reset_index()
        df.columns = ['İl', 'Don Skoru', 'Don Seviyesi', 'Kuraklık Skoru', 'Kuraklık Seviyesi', 'Yağış Skoru', 'Yağış Seviyesi']
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.info("💡 Harita görselleştirmeleri GitHub deponuza eklendikçe burada görünecektir.")
        # Eğer harita .png dosyaların GitHub'daysa şu kodu aktif edebilirsin:
        # st.image("don_haritasi.png", caption="Don Risk Haritası")

else:
    st.error("❌ 'tarlaiq_data.json' dosyası bulunamadı. Lütfen Colab'dan indirdiğiniz dosyayı GitHub deponuza yükleyin.")

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.success(f"Şu an aktif il: {secilen_il}")
st.sidebar.info("""
**TarlaIQ Nedir?**
Çiftçiler ve tarım paydaşları için iklim verilerini (sıcaklık, yağış, evaporasyon) kullanarak risk skorları üreten bir karar destek sistemidir.
""")
