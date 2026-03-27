"""
TBM İzleme Sayfası — Blue Line TN07
Güzergah: LandXML (DUb DLTM / EPSG:3997)
Her halka: 1.8 m
Halka başlangıç chainagei: 308+771.62 m
"""

import math
import xml.etree.ElementTree as ET

import folium
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(page_title="TBM İzleme", layout="wide", page_icon="🚇")

# ──────────────────────────────────────────────────────────
#  SABİTLER
# ──────────────────────────────────────────────────────────
HALKA_UZUNLUK   = 1.8        # m / halka
HALKA_BASLANGIC_CH = 308_771.62  # m  (308+771.62)
EPSG_PROJE      = 3997
TBM_CAPI        = 6.5        # görsel daire yarıçapı (m)

# ──────────────────────────────────────────────────────────
#  LANDXML VERİSİ  — TN07
# ──────────────────────────────────────────────────────────
LANDXML_TN07 = r"""<LandXML xmlns="http://www.landxml.org/schema/LandXML-1.2" version="1.2">
<Alignments>
<Alignment name="RLE _TN07_1" length="1426.448145256" staStart="307557.958300000" state="proposed">
<CoordGeom name="RLE _TN07_1" state="proposed">

<Line length="802.056000000" dir="3.388637062" staStart="307557.958300000">
  <Start>2785391.237538632 507777.352116356 0.0</Start>
  <End>2784613.532428970 507581.218005246 0.0</End>
</Line>

<Spiral length="63.977592461" radiusEnd="399.924000000" radiusStart="INF" rot="ccw"
  spiType="clothoid" dirStart="3.388637062" dirEnd="3.308649874" staStart="308360.014300000">
  <Start>2784613.532428970 507581.218005246 0.0</Start>
  <End>2784551.119968936 507567.236233594 0.0</End>
</Spiral>

<Curve rot="ccw" crvType="arc" length="288.892048276"
  dirStart="3.308649874" dirEnd="2.586282503" radius="399.924000000">
  <Start>2784551.119968936 507567.236233594 0.0</Start>
  <Center>2784484.620101668 507961.592637662 0.0</Center>
  <End>2784273.777420651 507621.762430591 0.0</End>
</Curve>

<Spiral length="63.977592510" radiusEnd="INF" radiusStart="399.924000000" rot="ccw"
  spiType="clothoid" dirStart="2.586282503" dirEnd="2.506295315" staStart="308712.883940738">
  <Start>2784273.777420651 507621.762430591 0.0</Start>
  <End>2784221.303310298 507658.331172090 0.0</End>
</Spiral>

<Line length="207.544912009" dir="2.506295315" staStart="308776.861533247">
  <Start>2784221.303310298 507658.331172090 0.0</Start>
  <End>2784054.251388929 507781.491823548 0.0</End>
</Line>

</CoordGeom>
</Alignment>
</Alignments>
</LandXML>"""


# ──────────────────────────────────────────────────────────
#  GÜZERGAH SINIFI
# ──────────────────────────────────────────────────────────
class Guzergah:
    """
    LandXML güzergahını parse eder.

    Koordinat sistemi:  (N, E) — (Northing, Easting)
    Yön:               azimut — kuzeyden saat yönünde, radyan
    Yay (Curve):       standart matematik açısı (atan2(N-Nc, E-Ec)) kullanılır
                       ccw → açı artar  |  cw → açı azalır
    Spiral:            başlangıç-bitiş noktaları arası lineer interpolasyon
                       (max sapma ~1.7 m — görsel için yeterli)
    """

    def __init__(self, xml_str: str):
        self.elemanlar: list[dict] = []
        self.sta_bas = 0.0
        self.uzunluk = 0.0
        self._parse(xml_str)
        self.cizgi = self._uret_cizgi(adim=3.0)

    # ── parse ──────────────────────────────────────────────
    def _parse(self, xml_str: str):
        xml_str = xml_str.replace(
            ' xmlns="http://www.landxml.org/schema/LandXML-1.2"', ""
        )
        kok = ET.fromstring(xml_str)
        hizalama = kok.find(".//Alignment")
        self.sta_bas = float(hizalama.get("staStart"))
        self.uzunluk = float(hizalama.get("length"))

        simdiki = self.sta_bas
        for e in hizalama.find("CoordGeom"):
            tag = e.tag

            if tag == "Line":
                uzun = float(e.get("length"))
                sta  = float(e.get("staStart", simdiki))
                self.elemanlar.append({
                    "tip": "Line",
                    "sta": sta, "uzun": uzun,
                    "bas": self._p(e, "Start"),
                    "son": self._p(e, "End"),
                    "yon": float(e.get("dir")),
                })
                simdiki = sta + uzun

            elif tag == "Curve":
                uzun = float(e.get("length"))
                self.elemanlar.append({
                    "tip": "Curve",
                    "sta": simdiki, "uzun": uzun,
                    "bas":    self._p(e, "Start"),
                    "son":    self._p(e, "End"),
                    "merkez": self._p(e, "Center"),
                    "R":      float(e.get("radius")),
                    "donus":  e.get("rot"),          # 'ccw' | 'cw'
                    "yonBas": float(e.get("dirStart")),
                })
                simdiki += uzun

            elif tag == "Spiral":
                uzun = float(e.get("length"))
                sta  = float(e.get("staStart", simdiki))
                rS   = e.get("radiusStart", "INF")
                rE   = e.get("radiusEnd",   "INF")
                self.elemanlar.append({
                    "tip":    "Spiral",
                    "sta": sta, "uzun": uzun,
                    "bas":    self._p(e, "Start"),
                    "son":    self._p(e, "End"),
                    "donus":  e.get("rot"),
                    "rBas":   float("inf") if rS == "INF" else float(rS),
                    "rSon":   float("inf") if rE == "INF" else float(rE),
                    "yonBas": float(e.get("dirStart")),
                    "yonSon": float(e.get("dirEnd")),
                })
                simdiki = sta + uzun

    @staticmethod
    def _p(elem, child_tag):
        """XML child element'inden (N, E) tuple'ı okur."""
        parts = elem.find(child_tag).text.strip().split()
        return (float(parts[0]), float(parts[1]))

    # ── interpolasyon ──────────────────────────────────────
    def konum(self, ch: float):
        """Chainage → (N, E) ya da None."""
        for e in self.elemanlar:
            sta_s = e["sta"]
            sta_e = sta_s + e["uzun"]
            if not (sta_s <= ch <= sta_e + 1e-6):
                continue
            off = ch - sta_s

            if e["tip"] == "Line":
                t = off / e["uzun"]
                N = e["bas"][0] + t * (e["son"][0] - e["bas"][0])
                E = e["bas"][1] + t * (e["son"][1] - e["bas"][1])
                return N, E

            elif e["tip"] == "Curve":
                Nc, Ec = e["merkez"]
                Ns, Es = e["bas"]
                R      = e["R"]
                # standart matematik açısı: atan2(y, x) = atan2(N-Nc, E-Ec)
                alfa0  = math.atan2(Ns - Nc, Es - Ec)
                sign   = 1 if e["donus"] == "ccw" else -1
                alfa   = alfa0 + sign * (off / R)
                return Nc + R * math.sin(alfa), Ec + R * math.cos(alfa)

            elif e["tip"] == "Spiral":
                t = off / e["uzun"]
                N = e["bas"][0] + t * (e["son"][0] - e["bas"][0])
                E = e["bas"][1] + t * (e["son"][1] - e["bas"][1])
                return N, E
        return None

    def azimut(self, ch: float) -> float:
        """Chainage → azimut (kuzeyden saat yönünde, radyan)."""
        for e in self.elemanlar:
            sta_s = e["sta"]
            sta_e = sta_s + e["uzun"]
            if not (sta_s <= ch <= sta_e + 1e-6):
                continue
            off = ch - sta_s

            if e["tip"] == "Line":
                return e["yon"]
            elif e["tip"] == "Curve":
                # ccw → azimut azalır (sola dönüş)
                sign = -1 if e["donus"] == "ccw" else 1
                return e["yonBas"] + sign * (off / e["R"])
            elif e["tip"] == "Spiral":
                t = off / e["uzun"]
                return e["yonBas"] + t * (e["yonSon"] - e["yonBas"])
        return 0.0

    def tbm_konumu(self, halka_no: int):
        """Halka no → (N, E, azimut_rad, chainage) ya da None."""
        ch = HALKA_BASLANGIC_CH + halka_no * HALKA_UZUNLUK
        pt = self.konum(ch)
        if pt is None:
            return None
        return pt[0], pt[1], self.azimut(ch), ch

    def _uret_cizgi(self, adim=3.0) -> list[tuple]:
        """Güzergahı adım aralıklı noktalara böler → [(N, E, ch), ...]"""
        pts = []
        sta_son = self.sta_bas + self.uzunluk
        ch = self.sta_bas
        while ch <= sta_son:
            pt = self.konum(ch)
            if pt:
                pts.append((pt[0], pt[1], ch))
            ch += adim
        pt = self.konum(sta_son)
        if pt:
            pts.append((pt[0], pt[1], sta_son))
        return pts


# ──────────────────────────────────────────────────────────
#  KOORDİNAT DÖNÜŞÜMÜ  (EPSG:3997 → WGS84)
# ──────────────────────────────────────────────────────────
@st.cache_resource
def _donusturucu():
    from pyproj import Transformer
    return Transformer.from_crs(EPSG_PROJE, 4326, always_xy=True)


def proje2wgs(N: float, E: float):
    """(N, E) proje coord → (lat, lon) WGS84. Hata → (None, None)."""
    try:
        t = _donusturucu()
        # always_xy=True: transform(x=E, y=N) → (lon, lat)
        lon, lat = t.transform(E, N)
        if -90 < lat < 90 and -180 < lon < 180:
            return lat, lon
    except Exception:
        pass
    return None, None


def guzergah_wgs84(cizgi: list[tuple]):
    """[(N,E,ch),...] → [[lat,lon],...] (geçersizleri atlar)"""
    out = []
    for N, E, _ in cizgi:
        la, lo = proje2wgs(N, E)
        if la is not None:
            out.append([la, lo])
    return out


# ──────────────────────────────────────────────────────────
#  UYGULAMA  ─  STREAMLIT UI
# ──────────────────────────────────────────────────────────
st.title("🚇 TBM İzleme — Blue Line TN07")

guzergah = Guzergah(LANDXML_TN07)

sta_son   = guzergah.sta_bas + guzergah.uzunluk
max_halka = int((sta_son - HALKA_BASLANGIC_CH) / HALKA_UZUNLUK)

# ── Üst bilgi kartları ────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Güzergah Uzunluğu",  f"{guzergah.uzunluk:.1f} m")
c2.metric("Halka Başlangıç Ch.", f"{HALKA_BASLANGIC_CH/1000:.3f} km")
c3.metric("Güzergah Bitiş Ch.", f"{sta_son/1000:.3f} km")
c4.metric("Tahmini Maks. Halka", max_halka)

st.divider()

# ── Halka girişi ──────────────────────────────────────────
halka_no = st.number_input(
    "🔢 Halka Numarası (Ring No)",
    min_value=0,
    max_value=max(max_halka + 50, 500),   # biraz tolerans
    value=0,
    step=1,
    help=f"Ring 0 → Ch {HALKA_BASLANGIC_CH:.2f} m  |  Ring {max_halka} → Ch {sta_son:.2f} m"
)

ch_tbm = HALKA_BASLANGIC_CH + halka_no * HALKA_UZUNLUK
konum  = guzergah.tbm_konumu(halka_no)

# ── TBM bilgi kartları ────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Halka No",          halka_no)
k2.metric("TBM Chainage",      f"{ch_tbm/1000:.4f} km")
k3.metric("İlerleme (halka başından)", f"{halka_no * HALKA_UZUNLUK:.1f} m")
if konum:
    yon_deg = math.degrees(konum[2]) % 360
    k4.metric("Yön (Azimut)", f"{yon_deg:.1f}°")
else:
    k4.metric("Yön (Azimut)", "—")

if ch_tbm > sta_son:
    st.warning(
        f"⚠️ Halka {halka_no} güzergah dışında  "
        f"(Ch {ch_tbm:.1f} m > bitiş {sta_son:.1f} m). "
        f"Harita son geçerli noktada durdu."
    )

st.divider()

# ── Harita ────────────────────────────────────────────────
if konum:
    N_tbm, E_tbm, yon_rad, ch = konum
    lat_tbm, lon_tbm = proje2wgs(N_tbm, E_tbm)

    if lat_tbm is not None:
        # Temel harita
        m = folium.Map(
            location=[lat_tbm, lon_tbm],
            zoom_start=17,
            tiles="OpenStreetMap"
        )

        # Uydu katmanı (toggle)
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/"
                  "World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri", name="Uydu", overlay=False, control=True
        ).add_to(m)
        folium.TileLayer("OpenStreetMap", name="Sokak Haritası").add_to(m)

        # Güzergah çizgisi
        cizgi_wgs = guzergah_wgs84(guzergah.cizgi)
        if cizgi_wgs:
            folium.PolyLine(
                cizgi_wgs,
                color="#1565C0", weight=5, opacity=0.85,
                tooltip="TN07 Tünel Güzergahı"
            ).add_to(m)

        # Başlangıç şaftı
        bas_pt = guzergah.konum(guzergah.sta_bas)
        if bas_pt:
            la, lo = proje2wgs(*bas_pt)
            if la:
                folium.Marker(
                    [la, lo],
                    tooltip=f"Başlangıç Şaftı  Ch: {guzergah.sta_bas/1000:.3f} km",
                    icon=folium.Icon(color="green", icon="home", prefix="fa")
                ).add_to(m)

        # Bitiş şaftı
        son_pt = guzergah.konum(sta_son)
        if son_pt:
            la, lo = proje2wgs(*son_pt)
            if la:
                folium.Marker(
                    [la, lo],
                    tooltip=f"Bitiş Şaftı  Ch: {sta_son/1000:.3f} km",
                    icon=folium.Icon(color="blue", icon="flag", prefix="fa")
                ).add_to(m)

        # TBM gövdesi — daire
        folium.Circle(
            location=[lat_tbm, lon_tbm],
            radius=TBM_CAPI / 2,
            color="#D32F2F", fill=True, fill_color="#EF5350",
            fill_opacity=0.7,
            tooltip=f"TBM | Ring: {halka_no} | Ch: {ch:.2f} m"
        ).add_to(m)

        # TBM yön oku — döndürülmüş ok işareti
        yon_css = (math.degrees(yon_rad)) % 360
        ok_html = (
            f'<div style="'
            f'  transform: rotate({yon_css:.1f}deg);'
            f'  font-size: 32px;'
            f'  color: #D32F2F;'
            f'  text-shadow: 1px 1px 3px #000;'
            f'  width: 36px; height: 36px;'
            f'  display: flex; align-items: center; justify-content: center;'
            f'">▲</div>'
        )
        folium.Marker(
            location=[lat_tbm, lon_tbm],
            icon=folium.DivIcon(html=ok_html, icon_size=(36, 36), icon_anchor=(18, 18)),
            tooltip=f"Ring {halka_no} | {yon_css:.1f}° | Ch {ch:.2f} m"
        ).add_to(m)

        folium.LayerControl().add_to(m)

        st_folium(m, width="100%", height=620, key="tbm_harita")

    else:
        # Koordinat dönüşümü başarısız → debug bilgisi
        st.error(
            f"⚠️ EPSG:{EPSG_PROJE} → WGS84 dönüşümü başarısız. "
            "EPSG kodunu veya proj4 parametrelerini doğrulayın."
        )
        st.info(
            f"**Ham proje koordinatları (EPSG:{EPSG_PROJE}):**\n\n"
            f"- N = `{N_tbm:.3f}`\n"
            f"- E = `{E_tbm:.3f}`\n\n"
            "Bir GIS uygulamasında (QGIS, AutoCAD) bu koordinatı açıp "
            "WGS84 karşılığını öğrenip buraya bildirin, "
            "koordinat sistemini düzeltiriz."
        )

        with st.expander("🔧 Tüm güzergah noktaları (ham)"):
            for N, E, sta in guzergah.cizgi[::10]:
                st.write(f"Ch {sta:.1f} m → N={N:.3f}, E={E:.3f}")
else:
    st.info(
        f"Ring {halka_no} güzergah tanımı dışında. "
        f"Geçerli aralık: 0 – {max_halka}"
    )
