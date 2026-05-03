import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Üretim Takip Pro v163", layout="wide")

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

# --- SMART THEME CSS (Gece Modu ve Büyük Rakam Uyumu) ---
st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"] > div {
        background-color: rgba(120, 120, 120, 0.1);
        border: 1px solid rgba(120, 120, 120, 0.3);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
    }
    /* Toplam Dakika Kutusu Tasarımı */
    .total-box {
        background-color: #0d47a1;
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        margin: 10px 0px;
    }
    .stButton > button {
        width: 100% !important;
        height: 50px;
        font-weight: bold;
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
    
    st.markdown("### 🚀 Üretim Detayları")
    
    with st.container():
        # Artikel Seçimi
        art_listesi = [""] + list(st.session_state["kutuphane"].keys())
        art_sec = st.selectbox("Artikel Numarası", options=art_listesi, index=0, key=f"art_{st.session_state['form_key']}")
        
        c1, c2 = st.columns(2)
        with c1:
            # Binler basamağı için step ve format ayarı
            adet = st.number_input("Adet (STK)", min_value=0, step=1, value=None, key=f"adet_{st.session_state['form_key']}")
            v_te = st.session_state["kutuphane"].get(art_sec, None)
            te_giris = st.number_input("TE Değeri", format="%.2f", value=v_te, key=f"te_{st.session_state['form_key']}")
            
        with c2:
            verim = st.number_input("Veri Prosent", min_value=0.01, format="%.2f", value=None, placeholder="Örn: 1.20", key=f"ver_{st.session_state['form_key']}")
            rust = st.number_input("Rüst (Dk)", min_value=0.0, value=None, key=f"rust_{st.session_state['form_key']}")
            gmk = st.number_input("GMK (Dk)", min_value=0.0, value=None, key=f"gmk_{st.session_state['form_key']}")

        # --- ANLIK HESAPLAMA KUTUSU ---
        toplam_is_dk = 0.0
        if adet and te_giris and verim:
            # Matematiksel işlem: (Adet * TE / Verim) + Ekler
            ara_hesap = (adet * te_giris) / verim
            toplam_is_dk = round(ara_hesap + (rust or 0) + (gmk or 0), 2)
            
            # Büyük Hesaplama Kutusu
            st.markdown(f"""
                <div class="total-box">
                    ⏱️ HESAPLANAN TOPLAM: {toplam_is_dk:,.2f} DK
                </div>
                """, unsafe_allow_html=True)
            
            # Hedef Durumu
            hedef_ref = 465 
            kalan = round(hedef_ref - (mevcut_toplam + toplam_is_dk), 2)
            if kalan > 0:
                st.warning(f"⚠️ Bu işten sonra hedef için kalan: {kalan:,.2f} dk")
            else:
                st.success(f"✅ Hedef tamamlanıyor! Fazla: {abs(kalan):,.2f} dk")

        notlar = st.text_area("Not / Auftrag", height=70, key=f"not_{st.session_state['form_key']}")

        st.markdown('<div class="main-btn">', unsafe_allow_html=True)
        if st.button("LİSTEYE EKLE VE HESAPLARI KAYDET"):
            if adet and te_giris and verim:
                yeni = {
                    "Tarih": datetime.now().strftime("%d.%m.%Y"),
                    "Artikel No": art_sec or "Manuel",
                    "Adet": int(adet),
                    "TE": round(te_giris, 2),
                    "Verim": verim,
                    "Toplam": toplam_is_dk,
                    "Not": notlar
                }
                st.session_state["liste"].insert(0, yeni)
                veri_kaydet(st.session_state["liste"], GUNCEL_LISTE_DOSYASI)
                st.session_state["form_key"] += 1
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- LİSTELEME BÖLÜMÜ ---
    if st.session_state["liste"]:
        st.markdown("### 📋 Günlük Üretim Listesi")
        df = pd.DataFrame(st.session_state["liste"])
        
        # Sayıları binlik ayraçla (1.210 gibi) gösteren tablo formatı
        st.dataframe(
            df[["Tarih", "Artikel No", "Adet", "TE", "Toplam", "Not"]].style.format({
                "Adet": "{:,.0f}",
                "TE": "{:.2f}",
                "Toplam": "{:,.2f}"
            }),
            use_container_width=True
        )
        
        t_biriken = df["Toplam"].sum()
        c_alt1, c_alt2 = st.columns(2)
        with c_alt1:
            h_giris = st.number_input("Günlük Hedef", value=465)
            st.metric("KALAN EKSİK", f"{h_giris - t_biriken:,.2f}")
        with c_alt2:
            st.write("")
            st.metric("GÜN TOPLAMI", f"{t_biriken:,.2f}")

        # Aksiyonlar
        col_a, col_s = st.columns(2)
        with col_a:
            if st.button("💾 GÜNÜ ARŞİVLE"):
                arsiv = veri_yukle(ARSIV_DOSYASI)
                arsiv.extend(st.session_state["liste"])
                veri_kaydet(arsiv, ARSIV_DOSYASI)
                st.session_state["liste"] = []
                veri_kaydet([], GUNCEL_LISTE_DOSYASI)
                st.rerun()
        with col_s:
            if st.button("🗑️ LİSTEYİ TEMİZLE"):
                st.session_state["liste"] = []
                veri_kaydet([], GUNCEL_LISTE_DOSYASI)
                st.rerun()

# Kütüphane ve Arşiv sekmeleri formata uygun korunmuştur.
