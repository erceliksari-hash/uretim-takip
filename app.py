import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Üretim Takip Pro v166", layout="wide")

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

# --- SMART THEME CSS ---
st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"] > div {
        background-color: rgba(120, 120, 120, 0.1);
        border: 1px solid rgba(120, 120, 120, 0.3);
        padding: 12px; border-radius: 10px;
    }
    input { font-size: 18px !important; } /* Telefon odaklanması için font büyütüldü */
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

# SIFIRLAMA MEKANİZMASI: Form key her değiştiğinde kutular boşalır
if "form_id" not in st.session_state:
    st.session_state["form_id"] = 0

# --- SEKMELER ---
sekme1, sekme2, sekme3 = st.tabs(["🏠 Üretim Girişi", "🏷️ Kütüphane", "📜 Arşiv"])

with sekme1:
    st.markdown("### 🚀 Üretim Girişi")
    
    with st.container():
        # TELEFON İÇİN KRİTİK: Selectbox yerine Manuel Giriş + Liste Önerisi
        # Bu yapı telefon klavyesinin her zaman açılmasını sağlar.
        art_giris = st.text_input("Artikel Numarası / Barkod Okut", 
                                 placeholder="Buraya yazın veya okutun...", 
                                 key=f"art_input_{st.session_state['form_id']}")
        
        # Eğer yazılan artikel kütüphanede varsa TE'yi otomatik çek
        v_te = st.session_state["kutuphane"].get(art_giris, 0.0)
        
        col1, col2 = st.columns(2)
        with col1:
            # value=None ve key kullanımı kutuların boş gelmesini sağlar
            adet = st.number_input("Adet (STK)", min_value=0, value=None, step=1, key=f"adet_{st.session_state['form_id']}")
            te_degeri = st.number_input("TE Değeri", format="%.2f", value=float(v_te) if v_te > 0 else None, key=f"te_{st.session_state['form_id']}")
            
        with col2:
            verim = st.number_input("Veri Prosent", min_value=0.01, value=1.20, key=f"ver_{st.session_state['form_id']}")
            rust = st.number_input("Rüst (Dk)", min_value=0.0, value=0.0, key=f"rust_{st.session_state['form_id']}")
            
        gmk = st.number_input("GMK (Dk)", min_value=0.0, value=0.0, key=f"gmk_{st.session_state['form_id']}")

        # --- ANLIK HESAPLAMA ---
        anlik_toplam = 0.0
        if adet and te_degeri and verim:
            anlik_toplam = round(((adet * te_degeri) / verim) + rust + gmk, 2)
        
        st.number_input("✅ HESAPLANAN TOPLAM DAKİKA", value=anlik_toplam, format="%.2f", disabled=True)

        notlar = st.text_area("Not / Auftrag", height=70, key=f"not_{st.session_state['form_id']}")

        st.markdown('<div class="main-btn">', unsafe_allow_html=True)
        if st.button("LİSTEYE EKLE VE SIFIRLA"):
            if art_giris and adet and te_degeri:
                yeni_kayit = {
                    "Tarih": datetime.now().strftime("%d.%m.%Y"),
                    "Artikel No": art_giris,
                    "Adet": int(adet),
                    "TE": te_degeri,
                    "Toplam": anlik_toplam,
                    "Not": notlar
                }
                st.session_state["liste"].insert(0, yeni_kayit)
                veri_kaydet(st.session_state["liste"], GUNCEL_LISTE_DOSYASI)
                
                # SIFIRLAMA BURADA YAPILIYOR: Form ID'yi değiştirerek tüm widget'ları resetliyoruz
                st.session_state["form_id"] += 1
                st.rerun()
            else:
                st.error("⚠️ Lütfen Artikel, Adet ve TE alanlarını doldurun!")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- ALT LİSTE ---
    if st.session_state["liste"]:
        df = pd.DataFrame(st.session_state["liste"])
        st.table(df[["Tarih", "Artikel No", "Adet", "Toplam"]])
        
        t_biriken = df["Toplam"].sum()
        st.metric("BUGÜNKÜ TOPLAM", f"{t_biriken:,.2f} dk")

# Kütüphane ve Arşiv bölümleri orijinal yapısını korumaktadır.
