import streamlit as st
import pandas as pd
import json
import os
import folium
from streamlit_folium import st_folium

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="TarlaIQ | Dr. Fatih", page_icon="🌱", layout="wide")

# --- KOORDİNAT VERİTABANI ---
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

@st.cache_data
def load_data():
    if os.path.exists('tarlaiq_data.json'):
        with open('tarlaiq_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

data = load_data()

# --- HAFIZA YÖNETİMİ (Session State) ---
# Selectbox ve Harita arasındaki bağı kuran ana değişken
if 'secilen_il' not in st.session_state:
    st.session_state['secilen_il'] = "Gümüşhane"

st.title("🌱 TarlaIQ: Akıllı Tarımsal Risk Platformu")

if data:
    iller = sorted(list(data.keys()))

    # --- ÜST PANEL (METRİKLER) ---
    col_secim, col_don, col_kurak, col_yagis = st.columns([1.5, 1, 1, 1])
    
    with col_secim:
        # ÖNEMLİ: Selectbox'ın indexini session_state'den alıyoruz
        # Manuel değişimde session_state'i güncellemek için on_change fonksiyonu eklenebilir ama index takibi yeterli
        current_il = st.selectbox(
            "📍 İl seçiniz:", 
            iller, 
            index=iller.index(st.session_state['secilen_il']),
            key="il_kutusu"
        )
        # Kutudan elle seçilirse hafızayı güncelle
        st.session_state['secilen_il'] = current_il

    # Rakamları session_state'deki güncel ile göre çek
    v = data[st.session_state['secilen_il']]
    
    with col_don:
        st.metric("Don Riski", f"%{v['don']}", v['don_seviye'], delta_color="inverse")
    with col_kurak:
        st.metric("Kuraklık Skoru", f"%{v['kuraklik']}", v['kuraklik_seviye'], delta_color="inverse")
    with col_yagis:
        st.metric("Yağış Skoru", v['yagis'], v['yagis_seviye'])

    st.divider()

    # --- İNTERAKTİF HARİTA ---
    # Haritayı oluştur
    m = folium.Map(location=[39.0, 35.5], zoom_start=6, tiles="CartoDB positron")

    for il_adi, skorlar in data.items():
        if il_adi in iller_koordinat:
            color = 'darkred' if skorlar['don'] >= 25 else 'orange' if skorlar['don'] >= 15 else 'green'
            folium.CircleMarker(
                location=iller_koordinat[il_adi],
                radius=10,
                tooltip=il_adi, # Harita takibi için tooltip kullanıyoruz
                color=color,
                fill=True,
                fill_opacity=0.7
            ).add_to(m)

    # Haritayı çiz ve çıktıyı al
    map_output = st_folium(m, width="100%", height=500, key="ana_harita")

    # --- SENKRONİZASYON TETİKLEYİCİSİ ---
    # Eğer haritadaki bir noktaya tıklanırsa
    if map_output and map_output.get("last_object_clicked_tooltip"):
        tıklanan_il = map_output["last_object_clicked_tooltip"]
        # Eğer tıklanan il, hafızadaki ilden farklıysa hafızayı güncelle ve sayfayı tazele
        if tıklanan_il != st.session_state['secilen_il']:
            st.session_state['secilen_il'] = tıklanan_il
            st.rerun() # Sayfa yeniden yüklenecek ve selectbox indexi yeni ile göre oluşacak

    st.divider()

    # --- ALT SEKMELER ---
    tab_list, tab_don, tab_kurak = st.tabs(["📊 Veri Tablosu", "❄️ Don Heatmap", "🌵 Kuraklık Heatmap"])
    
    with tab_list:
        df = pd.DataFrame.from_dict(data, orient='index').reset_index()
        df.columns = ['İl', 'Don Skoru', 'Don Seviyesi', 'Kuraklık Skoru', 'Kuraklık Seviyesi', 'Yağış Skoru', 'Yağış Seviyesi']
        st.dataframe(df.sort_values('Don Skoru', ascending=False), use_container_width=True, hide_index=True)

    with tab_don:
        if os.path.exists('don_haritasi.png'):
            st.image('don_haritasi.png', caption="Türkiye Don Risk Analizi", use_container_width=True)

    with tab_kurak:
        if os.path.exists('kuraklik_haritasi.png'):
            st.image('kuraklik_haritasi.png', caption="Türkiye Kuraklık Analizi", use_container_width=True)
else:
    st.error("Veri bulunamadı.")
