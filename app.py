import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Üretim Takip Pro v156", layout="wide")

# --- DOSYA DEPOLAMA ---
KUTUPHANE_DOSYASI = "artikel_kutuphanesi.csv"
ARSIV_DOSYASI = "uretim_arsivi.csv"
GUNCEL_LISTE_DOSYASI = "guncel_uretim.csv"

def veri_yukle(dosya_adi):
    if os.path.exists(dosya_adi):
        return pd.read_csv(dosya_adi).to_dict('records')
    return []

def veri_kaydet(liste, dosya_adi):
    if liste:
        pd.DataFrame(liste).to_csv(dosya_adi, index=False)
    else:
        if os.path.exists(dosya_adi):
            os.remove(dosya_adi)

# --- CSS (Mobil Uyumluluk) ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    div[data-testid="stVerticalBlock"] > div {
        background-color: #f6f8fa; border: 1px solid #d0d7de;
        padding: 12px; border-radius: 10px; margin-bottom: 5px;
    }
    .stButton > button { width: 100% !important; height: 50px; font-weight: bold; }
    .main-btn > div > button { background-color: #1f883d !important; color: white !important; }
    .archive-btn > div > button { background-color: #0969da !important; color: white !important; }
    .delete-btn > div > button { background-color: #cf222e !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
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
        # Artikel Seçimi
        art_sec = st.selectbox("Artikel Numarası", [""] + list(st.session_state["kutuphane"].keys()), 
                               index=0, key=f"art_{st.session_state['form_key']}")
        
        # Üst sıra: Adet ve Verim
        c1, c2 = st.columns(2)
        with c1:
            adet = st.number_input("Adet (STK)", min_value=0, value=None, key=f"adet_{st.session_state['form_key']}")
        with c2:
            verim = st.number_input("Veri Prosent (Örn: 1.0)", min_value=0.01, value=1.0, key=f"ver_{st.session_state['form_key']}")

        # Orta sıra: TE ve Rüst
        c3, c4 = st.columns(2)
        with c3:
            v_te = st.session_state["kutuphane"].get(art_sec, None)
            te_giris = st.number_input("TE Değeri", format="%.3f", value=v_te, key=f"te_{st.session_state['form_key']}")
        with c4:
            rust = st.number_input("Rüst (Dk)", min_value=0.0, value=0.0, key=f"rust_{st.session_state['form_key']}")

        # Alt sıra: GMK ve Not
        gmk = st.number_input("GMK (Dk)", min_value=0.0, value=0.0, key=f"gmk_{st.session_state['form_key']}")
        notlar = st.text_input("Not / Auftrag", key=f"not_{st.session_state['form_key']}")

        # OTOMATİK HESAPLAMA MANTIĞI
        toplam_dakika = 0.0
        if adet and te_giris:
            # Formül: (Adet * TE / Verim) + Rüst + GMK
            ana_sure = (adet * te_giris) / verim
            toplam_dakika = round(ana_sure + rust + gmk, 2)
            st.info(f"✨ Otomatik Hesaplanan: {toplam_dakika} dk")

        # EKLE BUTONU
        st.markdown('<div class="main-btn">', unsafe_allow_html=True)
        if st.button("LİSTEYE EKLE"):
            if adet and te_giris:
                yeni_kayit = {
                    "Tarih": datetime.now().strftime("%Y-%m-%d"),
                    "Artikel No": art_sec or "Manuel",
                    "Adet": int(adet),
                    "TE": round(te_giris, 3),
                    "Verim": round(verim, 2),
                    "Rüst": rust,
                    "GMK": gmk,
                    "Toplam": toplam_dakika,
                    "Not": notlar
                }
                st.session_state["liste"].insert(0, yeni_kayit)
                veri_kaydet(st.session_state["liste"], GUNCEL_LISTE_DOSYASI)
                st.session_state["form_key"] += 1 # Kutuları temizle
                st.rerun()
            else:
                st.error("Lütfen en az Adet ve TE giriniz!")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- LİSTE VE HEDEF ---
    if st.session_state["liste"]:
        df = pd.DataFrame(st.session_state["liste"])
        st.table(df[["Tarih", "Artikel No", "Adet", "Toplam", "Not"]]) # Özet tablo
        
        t_toplam = df["Toplam"].sum()
        col_k, col_t = st.columns(2)
        with col_k:
            hedef = st.number_input("Hedef (Dk)", value=465)
            st.metric("KALAN", f"{round(hedef - t_toplam, 2)}")
        with col_t:
            st.write("")
            st.metric("TOPLAM", f"{round(t_toplam, 2)}")

        # ARŞİVLE VE SİL
        st.markdown('<div class="archive-btn">', unsafe_allow_html=True)
        if st.button("GÜNÜ ARŞİVLE VE TEMİZLE"):
            arsiv = veri_yukle(ARSIV_DOSYASI)
            arsiv.extend(st.session_state["liste"])
            veri_kaydet(arsiv, ARSIV_DOSYASI)
            st.session_state["liste"] = []
            veri_kaydet([], GUNCEL_LISTE_DOSYASI)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
        if st.button("LİSTEYİ TAMAMEN SİL"):
            st.session_state["liste"] = []
            veri_kaydet([], GUNCEL_LISTE_DOSYASI)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

with sekme2:
    st.markdown("### 🏷️ Artikel Kütüphanesi")
    y_art = st.text_input("Yeni Artikel No").upper()
    y_te = st.number_input("Standart TE Değeri", format="%.3f", value=0.0)
    if st.button("Kütüphaneye Ekle"):
        if y_art and y_te > 0:
            st.session_state["kutuphane"][y_art] = y_te
            k_liste = [{"Artikel": k, "TE": v} for k, v in st.session_state["kutuphane"].items()]
            veri_kaydet(k_liste, KUTUPHANE_DOSYASI)
            st.success("Kaydedildi!")
            st.rerun()
    st.write("---")
    if st.session_state["kutuphane"]:
        st.dataframe(pd.DataFrame([{"Artikel": k, "TE": v} for k, v in st.session_state["kutuphane"].items()]))

with sekme3:
    st.markdown("### 📜 Üretim Arşivi")
    arsiv_verisi = veri_yukle(ARSIV_DOSYASI)
    if arsiv_verisi:
        df_arsiv = pd.DataFrame(arsiv_verisi)
        arama_tarih = st.date_input("Tarih Seç", datetime.now())
        t_str = arama_tarih.strftime("%Y-%m-%d")
        
        sonuc = df_arsiv[df_arsiv["Tarih"] == t_str]
        if not sonuc.empty:
            st.write(f"📅 {t_str} Tarihli Kayıtlar")
            st.dataframe(sonuc)
            st.metric("O Günün Toplamı", f"{sonuc['Toplam'].sum()}")
        else:
            st.warning("Bu tarihte kayıt bulunamadı.")
        
        if st.checkbox("Tüm Arşivi Göster"):
            st.dataframe(df_arsiv)
    else:
        st.info("Arşiv henüz boş.")
