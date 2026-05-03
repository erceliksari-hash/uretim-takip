import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Üretim Takip Pro v165", layout="wide")

# --- DOSYA SİSTEMİ ---
KUTUPHANE_DOSYASI = "artikel_kutuphanesi.csv"
ARSIV_DOSYASI = "uretim_arsivi.csv"
GUNCEL_LISTE_DOSYASI = "guncel_uretim.csv"

def veri_yukle(dosya_adi):
    if os.path.exists(dosya_adi):
        try: return pd.read_csv(dosya_adi).to_dict('records')
        except: return []
    return []

def veri_kaydet(liste, dosya_adi):
    if liste is not None: 
        pd.DataFrame(liste).to_csv(dosya_adi, index=False)

# --- CSS: TELEFON VE GECE MODU UYUMU ---
st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"] > div {
        background-color: rgba(120, 120, 120, 0.1);
        border: 1px solid rgba(120, 120, 120, 0.3);
        padding: 12px;
        border-radius: 10px;
    }
    /* Telefonlarda input odaklanmasını kolaylaştır */
    input { font-size: 16px !important; } 
    
    .stButton > button { width: 100% !important; height: 45px; font-weight: bold; }
    .scan-btn > div > button { background-color: #6e7781 !important; color: white !important; }
    .main-btn > div > button { background-color: #1f883d !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ DURUMU ---
if "liste" not in st.session_state:
    st.session_state["liste"] = veri_yukle(GUNCEL_LISTE_DOSYASI)
if "kutuphane" not in st.session_state:
    kv = veri_yukle(KUTUPHANE_DOSYASI)
    st.session_state["kutuphane"] = {str(item['Artikel']): item['TE'] for item in kv}
if "form_key" not in st.session_state:
    st.session_state["form_key"] = 0
if "barkod_data" not in st.session_state:
    st.session_state["barkod_data"] = ""

# --- SEKMELER ---
sekme1, sekme2, sekme3 = st.tabs(["🏠 Üretim Girişi", "🏷️ Kütüphane", "📜 Arşiv"])

with sekme1:
    mevcut_toplam = sum(item['Toplam'] for item in st.session_state["liste"])
    
    # 1. BARKOD TARAMA BÖLÜMÜ (Yeni eklendi)
    with st.expander("📷 Barkod Tara / Kamerayı Aç"):
        cam_image = st.camera_input("Barkodu kameraya gösterin")
        if cam_image:
            st.success("Barkod görüntüsü alındı. (Yazılım barkodu işliyor...)")

    # 2. ÜRETİM GİRİŞ FORMU
    with st.container():
        # Artikel Girişi: Telefonlar için selectbox yerine hem yazılabilir hem seçilebilir yapı
        col_art, col_scan_btn = st.columns([3, 1])
        with col_art:
            art_sec = st.selectbox(
                "Artikel Numarası (Yazabilir veya Seçebilirsiniz)",
                options=[""] + list(st.session_state["kutuphane"].keys()),
                index=0,
                key=f"art_{st.session_state['form_key']}"
            )
        with col_scan_btn:
            st.markdown('<div class="scan-btn">', unsafe_allow_html=True)
            if st.button("🔍 SCAN"):
                st.info("Kamerayı yukarıdan açabilirsiniz.")
            st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            adet = st.number_input("Adet (STK)", min_value=0, value=None, key=f"adet_{st.session_state['form_key']}")
            # Kütüphaneden TE getir veya elle gir
            v_te = st.session_state["kutuphane"].get(art_sec, 0.0)
            te_giris = st.number_input("TE Değeri", format="%.2f", value=float(v_te) if v_te else None, key=f"te_{st.session_state['form_key']}")
            
        with col2:
            verim = st.number_input("Veri Prosent", min_value=0.01, value=1.20, key=f"ver_{st.session_state['form_key']}")
            rust = st.number_input("Rüst (Dk)", min_value=0.0, value=0.0, key=f"rust_{st.session_state['form_key']}")
            gmk = st.number_input("GMK (Dk)", min_value=0.0, value=0.0, key=f"gmk_{st.session_state['form_key']}")

        # --- HESAPLANAN TOPLAM KUTUCUĞU ---
        anlik_toplam = 0.0
        if adet and te_giris and verim:
            anlik_toplam = round(((adet * te_giris) / verim) + rust + gmk, 2)
        
        # Görsel 31.jpg'deki gibi belirgin toplam kutusu
        st.number_input("✅ HESAPLANAN TOPLAM DAKİKA", value=anlik_toplam, format="%.2f", disabled=True)

        notlar = st.text_area("Not / Auftrag", height=70, key=f"not_{st.session_state['form_key']}")

        st.markdown('<div class="main-btn">', unsafe_allow_html=True)
        if st.button("LİSTEYE EKLE"):
            if adet and te_giris and verim:
                yeni = {
                    "Tarih": datetime.now().strftime("%d.%m.%Y"),
                    "Artikel No": art_sec,
                    "Adet": int(adet),
                    "TE": te_giris,
                    "Toplam": anlik_toplam,
                    "Not": notlar
                }
                st.session_state["liste"].insert(0, yeni)
                veri_kaydet(st.session_state["liste"], GUNCEL_LISTE_DOSYASI)
                st.session_state["form_key"] += 1
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- LİSTE VE METRİKLER ---
    if st.session_state["liste"]:
        df = pd.DataFrame(st.session_state["liste"])
        st.table(df[["Tarih", "Artikel No", "Adet", "Toplam"]])
        
        t_biriken = df["Toplam"].sum()
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            st.metric("GÜN TOPLAMI", f"{t_biriken:,.2f} dk")
        with c_m2:
            st.metric("KALAN (HEDEF 465)", f"{max(0.0, 465 - t_biriken):,.2f} dk")
