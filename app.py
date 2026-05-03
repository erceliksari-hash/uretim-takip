import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Üretim Takip Pro v161", layout="wide")

# --- DOSYA DEPOLAMA SİSTEMİ ---
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

# --- CSS TASARIMI ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    div[data-testid="stVerticalBlock"] > div {
        background-color: #f6f8fa; border: 1px solid #d0d7de;
        padding: 12px; border-radius: 10px; margin-bottom: 8px;
    }
    .stButton > button { width: 100% !important; height: 45px; font-weight: bold; border-radius: 6px; }
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
sekme1, sekme2, sekme3 = st.tabs(["🏠 Üretim Girişi", "🏷️ Artikel Kütüphanesi", "📜 Günlük Arşiv"])

with sekme1:
    # Mevcut listenin toplamını hesapla (Eksik dakika hesabı için)
    mevcut_toplam = sum(item['Toplam'] for item in st.session_state["liste"])
    
    st.markdown("### 🚀 Yeni İş Girişi")
    
    with st.container():
        # Artikel Seçimi
        art_listesi = [""] + list(st.session_state["kutuphane"].keys())
        art_sec = st.selectbox("Artikel Numarası", options=art_listesi, index=0, key=f"art_{st.session_state['form_key']}")
        
        col_sol, col_sag = st.columns(2)
        with col_sol:
            adet = st.number_input("Adet (STK)", min_value=0, value=None, key=f"adet_{st.session_state['form_key']}")
            v_te = st.session_state["kutuphane"].get(art_sec, None)
            te_giris = st.number_input("TE Değeri", format="%.2f", value=v_te, key=f"te_{st.session_state['form_key']}")
            
        with col_sag:
            verim = st.number_input("Veri Prosent", min_value=0.01, value=None, placeholder="Örn: 1.23", key=f"ver_{st.session_state['form_key']}")
            rust = st.number_input("Rüst (Dk)", min_value=0.0, value=None, key=f"rust_{st.session_state['form_key']}")
            gmk = st.number_input("GMK (Dk)", min_value=0.0, value=None, key=f"gmk_{st.session_state['form_key']}")

        # --- HESAPLAMA VE EKSİK DAKİKA GÖSTERGESİ ---
        toplam_is_dk = 0.0
        if adet and te_giris and verim:
            hesap = (adet * te_giris) / verim
            toplam_is_dk = round(hesap + (rust or 0) + (gmk or 0), 2)
            
            # Dinamik Bilgi Kutuları
            st.info(f"📊 **Bu İşin Toplamı:** {toplam_is_dk} dk")
            
            # Hedef varsayılan 465 üzerinden eksik hesapla (Liste dışı anlık)
            hedef_ref = 465 
            eksik_dk = round(hedef_ref - (mevcut_toplam + toplam_is_dk), 2)
            if eksik_dk > 0:
                st.warning(f"⚠️ **Bu İşten Sonra Kalan Eksik:** {eksik_dk} dk")
            else:
                st.success(f"✅ **Hedef Aşılıyor! Fazla:** {abs(eksik_dk)} dk")

        notlar = st.text_area("Not / Auftrag", height=70, key=f"not_{st.session_state['form_key']}")

        st.markdown('<div class="main-btn">', unsafe_allow_html=True)
        if st.button("LİSTEYE EKLE"):
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

    # --- ALT LİSTE VE GENEL DURUM ---
    if st.session_state["liste"]:
        st.write("---")
        df = pd.DataFrame(st.session_state["liste"])
        st.table(df[["Tarih", "Artikel No", "Adet", "TE", "Toplam"]])
        
        t_biriken = df["Toplam"].sum()
        c1, c2 = st.columns(2)
        with c1:
            hedef_input = st.number_input("Günlük Hedef (Dk)", value=465)
            st.metric("KALAN (EKSİK)", f"{round(hedef_input - t_biriken, 2)}")
        with c2:
            st.write("")
            st.metric("GÜNCEL TOPLAM", f"{round(t_biriken, 2)}")

        col_ars, col_sil = st.columns(2)
        with col_ars:
            if st.button("GÜNÜ ARŞİVLE VE TEMİZLE"):
                arsiv = veri_yukle(ARSIV_DOSYASI)
                arsiv.extend(st.session_state["liste"])
                veri_kaydet(arsiv, ARSIV_DOSYASI)
                st.session_state["liste"] = []
                veri_kaydet([], GUNCEL_LISTE_DOSYASI)
                st.rerun()
        with col_sil:
            if st.button("LİSTEYİ SİL"):
                st.session_state["liste"] = []
                veri_kaydet([], GUNCEL_LISTE_DOSYASI)
                st.rerun()

# Diğer sekmeler (Kütüphane ve Arşiv) kodun devamında aynen korunmuştur.
with sekme2:
    st.markdown("### 🏷️ Artikel Kütüphanesi")
    y_art = st.text_input("Artikel No").upper()
    y_te = st.number_input("Standart TE", format="%.2f")
    if st.button("Kaydet"):
        if y_art and y_te:
            st.session_state["kutuphane"][y_art] = y_te
            k_liste = [{"Artikel": k, "TE": v} for k, v in st.session_state["kutuphane"].items()]
            veri_kaydet(k_liste, KUTUPHANE_DOSYASI)
            st.success("Kaydedildi!")
            st.rerun()

with sekme3:
    st.markdown("### 🔍 Arşiv")
    arsiv_verisi = veri_yukle(ARSIV_DOSYASI)
    if arsiv_verisi:
        df_a = pd.DataFrame(arsiv_verisi)
        t_ara = st.date_input("Tarih Seç", datetime.now()).strftime("%d.%m.%Y")
        sonuc = df_a[df_a["Tarih"] == t_ara]
        if not sonuc.empty:
            st.table(sonuc)
