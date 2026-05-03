import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Üretim Takip Pro v167", layout="wide")

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

# --- CSS: GECE MODU VE TELEFON UYUMU ---
st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"] > div {
        background-color: rgba(120, 120, 120, 0.1);
        border: 1px solid rgba(120, 120, 120, 0.3);
        padding: 12px; border-radius: 10px;
    }
    input { font-size: 18px !important; color: inherit !important; }
    .stButton > button { width: 100% !important; height: 50px; font-weight: bold; }
    .main-btn > div > button { background-color: #1f883d !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ DURUMU ---
if "liste" not in st.session_state:
    st.session_state["liste"] = veri_yukle(GUNCEL_LISTE_DOSYASI)
if "kutuphane" not in st.session_state:
    kv = veri_yukle(KUTUPHANE_DOSYASI)
    st.session_state["kutuphane"] = {str(item['Artikel']): item['TE'] for item in kv}

# FORM SIFIRLAMA ANAHTARI
if "form_counter" not in st.session_state:
    st.session_state["form_counter"] = 0

# --- SEKMELER ---
sekme1, sekme2, sekme3 = st.tabs(["🏠 Üretim Girişi", "🏷️ Kütüphane", "📜 Arşiv"])

with sekme1:
    st.markdown("### 🚀 Yeni İş Girişi")
    f_id = st.session_state["form_counter"]
    
    with st.container():
        # ARTIKEL GİRİŞİ
        art_giris = st.text_input("Artikel Numarası / Barkod", placeholder="Yazın veya okutun...", key=f"art_{f_id}")
        
        # Kütüphaneden TE kontrolü
        v_te = st.session_state["kutuphane"].get(art_giris, "")

        col1, col2 = st.columns(2)
        with col1:
            # Kutuların boş gelmesi için hepsini text_input (mode=numeric) yapıyoruz
            adet_s = st.text_input("Adet (STK)", placeholder="Örn: 1210", key=f"adet_{f_id}")
            te_s = st.text_input("TE Değeri", value=str(v_te) if v_te else "", placeholder="Örn: 1.35", key=f"te_{f_id}")
            
        with col2:
            verim_s = st.text_input("Veri Prosent", placeholder="Örn: 1.20", key=f"ver_{f_id}")
            rust_s = st.text_input("Rüst (Dk)", placeholder="0.00", key=f"rust_{f_id}")
            
        gmk_s = st.text_input("GMK (Dk)", placeholder="0.00", key=f"gmk_{f_id}")

        # --- ANLIK HESAPLAMA (Metinden Sayıya Çevirerek) ---
        anlik_toplam = 0.0
        try:
            if adet_s and te_s and verim_s:
                calc_adet = float(adet_s)
                calc_te = float(te_s)
                calc_ver = float(verim_s)
                calc_rust = float(rust_s) if rust_s else 0.0
                calc_gmk = float(gmk_s) if gmk_s else 0.0
                
                anlik_toplam = round(((calc_adet * calc_te) / calc_ver) + calc_rust + calc_gmk, 2)
        except:
            anlik_toplam = 0.0

        # TOPLAM KUTUSU (Görseldeki gibi en altta)
        st.markdown(f"**✅ HESAPLANAN TOPLAM DAKİKA:** `{anlik_toplam:,.2f}`")

        notlar = st.text_area("Not / Auftrag", placeholder="İş emri...", key=f"not_{f_id}")

        st.markdown('<div class="main-btn">', unsafe_allow_html=True)
        if st.button("LİSTEYE EKLE VE KUTULARI BOŞALT"):
            if art_giris and adet_s and te_s and verim_s:
                yeni = {
                    "Tarih": datetime.now().strftime("%d.%m.%Y"),
                    "Artikel No": art_giris,
                    "Adet": adet_s,
                    "TE": te_s,
                    "Toplam": anlik_toplam,
                    "Not": notlar
                }
                st.session_state["liste"].insert(0, yeni)
                veri_kaydet(st.session_state["liste"], GUNCEL_LISTE_DOSYASI)
                
                # SAYACI ARTIR VE SAYFAYI YENİLE (Bu işlem tüm kutuları placeholder haline getirir)
                st.session_state["form_counter"] += 1
                st.rerun()
            else:
                st.error("⚠️ Lütfen boş alanları doldurun!")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- ALT LİSTE ---
    if st.session_state["liste"]:
        st.write("---")
        df = pd.DataFrame(st.session_state["liste"])
        st.table(df[["Tarih", "Artikel No", "Adet", "Toplam"]])
        st.metric("BUGÜNÜN TOPLAMI", f"{df['Toplam'].sum():,.2f} dk")

# Kütüphane ve Arşiv bölümleri orijinal yapısını korumaktadır.
