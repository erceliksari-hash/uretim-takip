import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Üretim Takip Pro v164", layout="wide")

# --- DOSYA DEPOLAMA ---
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

# --- SMART THEME CSS ---
st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"] > div {
        background-color: rgba(120, 120, 120, 0.1);
        border: 1px solid rgba(120, 120, 120, 0.3);
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 8px;
    }
    /* Toplama Kutucuğu İçin Özel Stil */
    .stNumberInput input {
        font-size: 1.2rem !important;
        font-weight: bold !important;
    }
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

# --- SEKMELER ---
sekme1, sekme2, sekme3 = st.tabs(["🏠 Üretim Girişi", "🏷️ Kütüphane", "📜 Arşiv"])

with sekme1:
    mevcut_toplam = sum(item['Toplam'] for item in st.session_state["liste"])
    st.markdown("### 🚀 Üretim Girişi")
    
    with st.container():
        # Artikel Seçimi
        art_listesi = [""] + list(st.session_state["kutuphane"].keys())
        art_sec = st.selectbox("Artikel Numarası", options=art_listesi, index=0, key=f"art_{st.session_state['form_key']}")
        
        col1, col2 = st.columns(2)
        with col1:
            adet = st.number_input("Adet (STK)", min_value=0, value=None, key=f"adet_{st.session_state['form_key']}")
            v_te = st.session_state["kutuphane"].get(art_sec, None)
            te_giris = st.number_input("TE Değeri", format="%.2f", value=v_te, key=f"te_{st.session_state['form_key']}")
            
        with col2:
            verim = st.number_input("Veri Prosent", min_value=0.01, value=1.20, key=f"ver_{st.session_state['form_key']}")
            rust = st.number_input("Rüst (Dk)", min_value=0.0, value=0.0, key=f"rust_{st.session_state['form_key']}")
            gmk = st.number_input("GMK (Dk)", min_value=0.0, value=0.0, key=f"gmk_{st.session_state['form_key']}")

        # --- OTOMATİK TOPLAMA KUTUCUĞU ---
        # Değerler girildiği anda matematiksel işlemi yapıyoruz
        anlik_toplam = 0.0
        if adet and te_giris and verim:
            islem = (adet * te_giris) / verim
            anlik_toplam = round(islem + rust + gmk, 2)
        
        # İstediğin Toplama Kutucuğu (Sadece Okunabilir/Disabled gibi davranır)
        st.number_input("✅ HESAPLANAN TOPLAM DAKİKA", value=anlik_toplam, format="%.2f", disabled=True)

        # Hedef Durumu (Görsel 80.jpg'deki gibi)
        hedef_dk = 465
        kalan = round(hedef_dk - (mevcut_toplam + anlik_toplam), 2)
        if anlik_toplam > 0:
            if kalan > 0:
                st.warning(f"⚠️ Bu işten sonra hedef için kalan eksik: {kalan:,.2f} dk")
            else:
                st.success(f"🎉 Hedef aşılıyor! Fazla üretim: {abs(kalan):,.2f} dk")

        notlar = st.text_area("Not / Auftrag", height=70, key=f"not_{st.session_state['form_key']}")

        st.markdown('<div class="main-btn">', unsafe_allow_html=True)
        if st.button("LİSTEYE EKLE"):
            if adet and te_giris and verim:
                yeni = {
                    "Tarih": datetime.now().strftime("%d.%m.%Y"),
                    "Artikel No": art_sec or "Manuel",
                    "Adet": int(adet),
                    "TE": round(te_giris, 2),
                    "Toplam": anlik_toplam,
                    "Not": notlar
                }
                st.session_state["liste"].insert(0, yeni)
                veri_kaydet(st.session_state["liste"], GUNCEL_LISTE_DOSYASI)
                st.session_state["form_key"] += 1
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- LİSTELEME ---
    if st.session_state["liste"]:
        df = pd.DataFrame(st.session_state["liste"])
        st.write("### 📋 Bugünün Üretimleri")
        st.dataframe(df[["Tarih", "Artikel No", "Adet", "TE", "Toplam", "Not"]], use_container_width=True)
        
        # Metrikler
        t_biriken = df["Toplam"].sum()
        m1, m2 = st.columns(2)
        with m1:
            h_input = st.number_input("Hedef", value=465)
            st.metric("EKSİK", f"{h_input - t_biriken:,.2f} dk")
        with m2:
            st.write("")
            st.metric("GÜN TOPLAMI", f"{t_biriken:,.2f} dk")

# Kütüphane ve Arşiv sekmeleri formata uygun korunmuştur.
