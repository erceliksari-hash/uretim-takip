import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Üretim Takip Pro v157", layout="wide")

# --- DOSYA DEPOLAMA SİSTEMİ (Korumalı) ---
KUTUPHANE_DOSYASI = "artikel_kutuphanesi.csv"
ARSIV_DOSYASI = "uretim_arsivi.csv"
GUNCEL_LISTE_DOSYASI = "guncel_uretim.csv"

def veri_yukle(dosya_adi):
    if os.path.exists(dosya_adi):
        try:
            return pd.read_csv(dosya_adi).to_dict('records')
        except:
            return []
    return []

def veri_kaydet(liste, dosya_adi):
    if liste:
        pd.DataFrame(liste).to_csv(dosya_adi, index=False)
    else:
        if os.path.exists(dosya_adi):
            os.remove(dosya_adi)

# --- CSS TASARIMI (Görsel 56.jpg ile birebir uyumlu) ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    div[data-testid="stVerticalBlock"] > div {
        background-color: #f6f8fa;
        border: 1px solid #d0d7de;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .stButton > button {
        width: 100% !important;
        height: 45px;
        font-weight: bold;
        border-radius: 6px;
    }
    /* Buton Renkleri */
    .main-btn > div > button { background-color: #1f883d !important; color: white !important; }
    .archive-btn > div > button { background-color: #0969da !important; color: white !important; }
    .delete-btn > div > button { background-color: #cf222e !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ DURUMU ---
if "liste" not in st.session_state:
    st.session_state["liste"] = veri_yukle(GUNCEL_LISTE_DOSYASI)
if "kutuphane" not in st.session_state:
    kv = veri_yukle(KUTUPHANE_DOSYASI)
    st.session_state["kutuphane"] = {item['Artikel']: item['TE'] for item in kv}
if "form_key" not in st.session_state:
    st.session_state["form_key"] = 0

# --- SEKMELER ---
sekme1, sekme2, sekme3 = st.tabs(["🏠 Üretim Girişi", "🏷️ Artikel Kütüphanesi", "📜 Günlük Arşiv"])

with sekme1:
    st.markdown("### 🚀 Yeni İş Girişi")
    
    with st.container():
        # 1. Satır: Artikel Numarası (Tam Genişlik)
        art_sec = st.selectbox("Artikel Numarası", [""] + list(st.session_state["kutuphane"].keys()), 
                               index=0, key=f"art_{st.session_state['form_key']}")
        
        # 2. Satır: Adet ve Veri Prosent (Yan Yana)
        c1, c2 = st.columns(2)
        with c1:
            adet = st.number_input("Adet (STK)", min_value=0, value=None, key=f"adet_{st.session_state['form_key']}")
        with c2:
            verim = st.number_input("Veri Prosent", min_value=0.01, value=None, placeholder="Örn: 1.23", key=f"ver_{st.session_state['form_key']}")

        # 3. Satır: TE Değeri ve Rüst (Yan Yana)
        c3, c4 = st.columns(2)
        with c3:
            v_te = st.session_state["kutuphane"].get(art_sec, None)
            te_giris = st.number_input("TE Değeri", format="%.3f", value=v_te, key=f"te_{st.session_state['form_key']}")
        with c4:
            rust = st.number_input("Rüst (Dk)", min_value=0.0, value=None, key=f"rust_{st.session_state['form_key']}")

        # 4. Satır: GMK
        gmk = st.number_input("GMK (Dk)", min_value=0.0, value=None, key=f"gmk_{st.session_state['form_key']}")
        
        # 5. Satır: Not
        notlar = st.text_input("Not / Auftrag", key=f"not_{st.session_state['form_key']}")

        # --- OTOMATİK HESAPLAMA MANTIĞI ---
        toplam_is_dk = 0.0
        # Eğer Adet, TE ve Verim girilmişse hesapla
        if adet and te_giris and verim:
            # Formül: (Adet * TE / Verim) + Rüst + GMK
            r_val = rust if rust else 0
            g_val = gmk if gmk else 0
            hesap = (adet * te_giris) / verim
            toplam_is_dk = round(hesap + r_val + g_val, 2)
            
            st.info(f"✨ Hesaplanan: {toplam_is_dk} dk")

        # 6. Satır: Liste Ekle Butonu
        st.markdown('<div class="main-btn">', unsafe_allow_html=True)
        if st.button("LİSTEYE EKLE"):
            if adet and te_giris and verim:
                yeni = {
                    "Tarih": datetime.now().strftime("%Y-%m-%d"),
                    "Artikel No": art_sec or "Manuel",
                    "Adet": int(adet),
                    "TE": round(te_giris, 3),
                    "Verim": verim,
                    "Toplam": toplam_is_dk,
                    "Not": notlar
                }
                st.session_state["liste"].insert(0, yeni)
                veri_kaydet(st.session_state["liste"], GUNCEL_LISTE_DOSYASI)
                st.session_state["form_key"] += 1 # Kutuları temizle
                st.rerun()
            else:
                st.error("Lütfen Adet, Verim ve TE alanlarını doldurun!")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- GÜNLÜK LİSTE VE HEDEF TABLOSU ---
    if st.session_state["liste"]:
        st.markdown("### 📊 Günlük Liste")
        df = pd.DataFrame(st.session_state["liste"])
        st.table(df[["Tarih", "Artikel No", "Adet", "Toplam", "Not"]])
        
        t_biriken = df["Toplam"].sum()
        col_kalan, col_toplam = st.columns(2)
        with col_kalan:
            hedef = st.number_input("Hedef Dakika", value=465)
            st.metric("KALAN", f"{round(hedef - t_biriken, 2)}")
        with col_toplam:
            st.write("")
            st.metric("ŞU ANKİ TOPLAM", f"{round(t_biriken, 2)}")

        # ARŞİV VE SİLME BUTONLARI
        c_alt1, c_alt2 = st.columns(2)
        with c_alt1:
            st.markdown('<div class="archive-btn">', unsafe_allow_html=True)
            if st.button("GÜNÜ ARŞİVLE"):
                arsiv = veri_yukle(ARSIV_DOSYASI)
                arsiv.extend(st.session_state["liste"])
                veri_kaydet(arsiv, ARSIV_DOSYASI)
                st.session_state["liste"] = []
                veri_kaydet([], GUNCEL_LISTE_DOSYASI)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with c_alt2:
            st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
            if st.button("LİSTEYİ SİL"):
                st.session_state["liste"] = []
                veri_kaydet([], GUNCEL_LISTE_DOSYASI)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- 🏷️ KÜTÜPHANE SEKİMESİ ---
with sekme2:
    st.markdown("### 🏷️ Artikel Kaydı")
    y_art = st.text_input("Artikel No").upper()
    y_te = st.number_input("Standart TE", format="%.3f", value=0.0)
    if st.button("Kütüphaneye Kaydet"):
        if y_art and y_te > 0:
            st.session_state["kutuphane"][y_art] = y_te
            k_verisi = [{"Artikel": k, "TE": v} for k, v in st.session_state["kutuphane"].items()]
            veri_kaydet(k_verisi, KUTUPHANE_DOSYASI)
            st.success("Kaydedildi!")
            st.rerun()
    
    if st.session_state["kutuphane"]:
        st.write("---")
        st.dataframe(pd.DataFrame([{"Artikel": k, "TE": v} for k, v in st.session_state["kutuphane"].items()]))

# --- 📜 ARŞİV SEKMESİ ---
with sekme3:
    st.markdown("### 🔍 Geçmiş Üretimler")
    arsiv_data = veri_yukle(ARSIV_DOSYASI)
    if arsiv_data:
        df_arsiv = pd.DataFrame(arsiv_data)
        sec_tarih = st.date_input("Tarih Seç", datetime.now())
        t_ara = sec_tarih.strftime("%Y-%m-%d")
        
        filtre = df_arsiv[df_arsiv["Tarih"] == t_ara]
        if not filtre.empty:
            st.table(filtre)
            st.metric("Gün Toplamı", f"{filtre['Toplam'].sum()}")
        else:
            st.warning("Bu tarihte kayıt yok.")
        
        if st.checkbox("Tüm Arşivi Listele"):
            st.dataframe(df_arsiv)
    else:
        st.info("Arşiv henüz boş.")
