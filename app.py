import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Üretim Takip Pro v155", layout="wide")

# --- DOSYA TABANLI DEPOLAMA SİSTEMİ ---
# Verilerin telefon kapansa bile silinmemesi için CSV dosyalarına kaydediyoruz
KUTUPHANE_DOSYASI = "artikel_kutuphanesi.csv"
ARSIV_DOSYASI = "uretim_arsivi.csv"
GUNCEL_LISTE_DOSYASI = "guncel_uretim.csv"

def veri_yukle(dosya_adi):
    if os.path.exists(dosya_adi):
        return pd.read_csv(dosya_adi).to_dict('records')
    return []

def veri_kaydet(liste, dosya_adi):
    df = pd.DataFrame(liste)
    df.to_csv(dosya_adi, index=False)

# --- CSS TASARIMI (Mobil Uyumluluk Artırıldı) ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1f2328; }
    div[data-testid="stVerticalBlock"] > div {
        background-color: #f6f8fa; border: 1px solid #d0d7de;
        padding: 15px; border-radius: 10px; margin-bottom: 10px;
    }
    .stButton > button { width: 100% !important; height: 50px; border-radius: 8px; font-weight: bold; }
    .main-btn > div > button { background-color: #1f883d !important; color: white !important; }
    .archive-btn > div > button { background-color: #0969da !important; color: white !important; }
    .delete-btn > div > button { background-color: #cf222e !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- OTURUM BAŞLATMA ---
if "liste" not in st.session_state:
    st.session_state["liste"] = veri_yukle(GUNCEL_LISTE_DOSYASI)
if "kutuphane" not in st.session_state:
    # Kütüphaneyi hızlı erişim için sözlüğe çeviriyoruz
    veriler = veri_yukle(KUTUPHANE_DOSYASI)
    st.session_state["kutuphane"] = {item['Artikel']: item['TE'] for item in veriler}
if "form_key" not in st.session_state:
    st.session_state["form_key"] = 0

# --- ÜST MENÜ ---
sekme1, sekme2, sekme3 = st.tabs(["🏠 Üretim Girişi", "🏷️ Artikel Kütüphanesi", "📜 Günlük Arşiv"])

# --- 🏠 ÜRETİM GİRİŞİ SEKMESİ ---
with sekme1:
    st.markdown("### 🚀 Yeni İş Girişi")
    
    with st.container():
        art_sec = st.selectbox("Artikel Numarası", [""] + list(st.session_state["kutuphane"].keys()), 
                               index=0, key=f"art_{st.session_state['form_key']}")
        
        c1, c2 = st.columns(2)
        with c1:
            adet = st.number_input("Adet (STK)", min_value=0, value=None, key=f"adet_{st.session_state['form_key']}")
            varsayilan_te = st.session_state["kutuphane"].get(art_sec, None)
            te_giris = st.number_input("TE Değeri", format="%.3f", value=varsayilan_te, key=f"te_{st.session_state['form_key']}")
        with c2:
            verim = st.number_input("Veri Prosent", min_value=0.1, value=None, key=f"ver_{st.session_state['form_key']}")
            rust = st.number_input("Rüst (Dk)", min_value=0, value=None, key=f"rust_{st.session_state['form_key']}")

        gmk = st.number_input("GMK (Dk)", min_value=0, value=None, key=f"gmk_{st.session_state['form_key']}")
        notlar = st.text_input("Not / Auftrag", key=f"not_{st.session_state['form_key']}")

        if adet and te_giris:
            v_oran = verim if verim else 1.0
            toplam_is_dk = round(((adet * te_giris) / v_oran) + (rust or 0) + (gmk or 0), 2)
            st.info(f"Hesaplanan: {toplam_is_dk} dk")

        st.markdown('<div class="main-btn">', unsafe_allow_html=True)
        if st.button("LİSTEYE EKLE"):
            if adet and te_giris:
                yeni = {
                    "Tarih": datetime.now().strftime("%Y-%m-%d"),
                    "Artikel No": art_sec or "Manuel",
                    "Adet": int(adet),
                    "TE": round(te_giris, 1),
                    "Verim": int(verim) if verim else 1,
                    "Rüst": rust or 0, "GMK": gmk or 0, "Toplam": toplam_is_dk, "Not": notlar
                }
                st.session_state["liste"].insert(0, yeni)
                veri_kaydet(st.session_state["liste"], GUNCEL_LISTE_DOSYASI) # ANLIK KAYIT
                st.session_state["form_key"] += 1
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state["liste"]:
        df = pd.DataFrame(st.session_state["liste"])
        st.table(df)
        
        toplam_biriken = df["Toplam"].sum()
        c_alt1, c_alt2 = st.columns(2)
        with c_alt1:
            hedef = st.number_input("Hedef", value=465)
            st.metric("KALAN", f"{hedef - toplam_biriken:.2f}")
        with c_alt2:
            st.write("")
            st.metric("TOPLAM", f"{toplam_biriken:.2f}")

        # AKSİYONLAR
        st.markdown('<div class="archive-btn">', unsafe_allow_html=True)
        if st.button("GÜNÜ ARŞİVLE VE TEMİZLE"):
            mevcut_arsiv = veri_yukle(ARSIV_DOSYASI)
            mevcut_arsiv.extend(st.session_state["liste"])
            veri_kaydet(mevcut_arsiv, ARSIV_DOSYASI) # ARŞİVE KAYDET
            st.session_state["liste"] = []
            veri_kaydet([], GUNCEL_LISTE_DOSYASI) # GÜNCELİ TEMİZLE
            st.rerun()
        st.markdown('</div><div class="delete-btn">', unsafe_allow_html=True)
        if st.button("LİSTEYİ SİL"):
            st.session_state["liste"] = []
            veri_kaydet([], GUNCEL_LISTE_DOSYASI)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 🏷️ ARTIKEL KÜTÜPHANESİ ---
with sekme2:
    st.markdown("### 🏷️ Kütüphane Yönetimi")
    y_ad = st.text_input("Artikel No").upper()
    y_te = st.number_input("Standart TE", format="%.3f", value=None)
    if st.button("Kütüphaneye Kaydet"):
        if y_ad and y_te:
            st.session_state["kutuphane"][y_ad] = y_te
            # Sözlüğü listeye çevirip kaydet
            liste_halinde = [{"Artikel": k, "TE": v} for k, v in st.session_state["kutuphane"].items()]
            veri_kaydet(liste_halinde, KUTUPHANE_DOSYASI)
            st.success("Kütüphane güncellendi!")
            st.rerun()
    
    if st.session_state["kutuphane"]:
        st.write("---")
        st.table(pd.DataFrame([{"Artikel": k, "TE": v} for k, v in st.session_state["kutuphane"].items()]))

# --- 📜 GÜNLÜK ARŞİV ---
with sekme3:
    arsiv_verileri = veri_yukle(ARSIV_DOSYASI)
    if arsiv_verileri:
        df_arsiv = pd.DataFrame(arsiv_verileri)
        sec_tarih = st.date_input("Tarih ile Filtrele", datetime.now())
        tarih_s = sec_tarih.strftime("%Y-%m-%d")
        
        sonuc = df_arsiv[df_arsiv["Tarih"] == tarih_s]
        if not sonuc.empty:
            st.table(sonuc)
            st.metric("O Günün Toplamı", f"{sonuc['Toplam'].sum():.2f}")
        else:
            st.warning("Bu tarihte kayıt yok.")
        
        if st.checkbox("Tüm Arşivi Göster"):
            st.dataframe(df_arsiv)
    else:
        st.info("Arşiv henüz boş.")
