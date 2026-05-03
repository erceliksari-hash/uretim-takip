import streamlit as st
import pandas as pd
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Üretim Takip Pro v153", layout="wide")

# --- CSS TASARIMI ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1f2328; }
    [data-testid="stSidebar"] { display: none; }
    div[data-testid="stVerticalBlock"] > div {
        background-color: #f6f8fa;
        border: 1px solid #d0d7de;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    div.stButton > button:first-child {
        background-color: #1f883d;
        color: white;
        font-weight: bold;
        width: 100%;
        height: 45px;
        border-radius: 6px;
    }
    h3 { color: #0969da !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ŞİFRE KONTROLÜ (SECRETS) ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown("<h2 style='text-align: center;'>🔐 Giriş</h2>", unsafe_allow_html=True)
    c1, col_login, c3 = st.columns([1,1,1])
    with col_login:
        dogru_sifre = st.secrets["GIRIS_SIFRESI"]
        s_input = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap"):
            if s_input == dogru_sifre:
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("❌ Hatalı Şifre!")
    st.stop()

# --- VERİ VE SIFIRLAMA YAPISI ---
if "liste" not in st.session_state:
    st.session_state["liste"] = []
if "kutuphane" not in st.session_state:
    st.session_state["kutuphane"] = {}

# Kutuları sıfırlamak için bir sayaç kullanıyoruz
if "form_key" not in st.session_state:
    st.session_state["form_key"] = 0

def form_sifirla():
    st.session_state["form_key"] += 1

# --- ÜST MENÜ ---
sekme1, sekme2, sekme3 = st.tabs(["🏠 Üretim Girişi", "🏷️ Artikel Kütüphanesi", "📜 Günlük Arşiv"])

# --- 🏠 ÜRETİM GİRİŞİ SEKMESİ ---
with sekme1:
    st.markdown("### 🚀 Yeni İş Girişi")
    
    # Her ekleme sonrası "form_key" değiştiği için widgetlar sıfırlanır
    with st.container():
        # 1. Satır: Artikel Seçimi
        art_sec = st.selectbox(
            "Artikel Numarası", 
            [""] + list(st.session_state["kutuphane"].keys()), 
            index=0,
            key=f"art_{st.session_state['form_key']}"
        )
        
        # 2. Satır: Adet, TE ve Veri Prosent
        col_adet, col_te, col_verim = st.columns(3)
        
        with col_adet:
            adet = st.number_input("Adet (STK)", min_value=0, value=None, placeholder="Miktar...", key=f"adet_{st.session_state['form_key']}")
        
        with col_te:
            # Kütüphaneden gelen varsayılan değer
            varsayilan_te = st.session_state["kutuphane"].get(art_sec, None) if art_sec != "" else None
            te_giris = st.number_input("TE Değeri", format="%.3f", value=varsayilan_te, placeholder="TE...", key=f"te_{st.session_state['form_key']}")
            
        with col_verim:
            verim = st.number_input("Veri Prosent (%)", min_value=0.1, value=None, placeholder="Örn: 1.0", key=f"ver_{st.session_state['form_key']}")

        # 3. Satır: Rüst, GMK ve Not
        c_r, c_g, c_n = st.columns(3)
        with c_r:
            rust = st.number_input("Rüst (Dk)", min_value=0, value=None, key=f"rust_{st.session_state['form_key']}")
        with c_g:
            gmk = st.number_input("GMK (Dk)", min_value=0, value=None, key=f"gmk_{st.session_state['form_key']}")
        with c_n:
            notlar = st.text_input("Not / Auftrag", placeholder="Not...", key=f"not_{st.session_state['form_key']}")

        # Toplam Dakika Hesaplama (Görsel geri bildirim için)
        toplam_is_dk = 0.0
        if adet is not None and te_giris is not None:
            v_oran = verim if verim is not None else 1.0
            r_val = rust if rust is not None else 0
            g_val = gmk if gmk is not None else 0
            net_dk = (adet * te_giris) / v_oran
            toplam_is_dk = round(net_dk + r_val + g_val, 2)
            st.info(f"Hesaplanan Toplam: {toplam_is_dk} dk")

        if st.button("LİSTEYE EKLE"):
            if adet is None or te_giris is None:
                st.warning("Adet ve TE girilmeden ekleme yapılamaz!")
            else:
                yeni = {
                    "Saat": datetime.now().strftime("%H:%M"),
                    "Artikel No": art_sec if art_sec != "" else "Manuel",
                    "Adet (STK)": adet,
                    "TE Değeri": te_giris,
                    "Veri Prosent": verim if verim is not None else 1.0,
                    "Rüst": rust if rust is not None else 0,
                    "GMK": gmk if gmk is not None else 0,
                    "Toplam Dakika": toplam_is_dk,
                    "Not": notlar
                }
                st.session_state["liste"].insert(0, yeni)
                # KUTULARI SIFIRLA:
                form_sifirla()
                st.rerun()

    # --- LİSTELEME VE HEDEF ÇIKARMA ---
    if st.session_state["liste"]:
        st.markdown("### 📊 Günlük Liste")
        df = pd.DataFrame(st.session_state["liste"])
        st.table(df)

        st.write("---")
        col_hesap1, col_hesap2 = st.columns(2)
        with col_hesap1:
            hedef_deger = st.number_input("Hedef Dakika", value=465)
            toplam_biriken = df["Toplam Dakika"].sum()
            st.metric("Şu Anki Toplam", f"{toplam_biriken:.2f}")
        with col_hesap2:
            kalan = hedef_deger - toplam_biriken
            st.metric("Kalan", f"{kalan:.2f}")

# --- 🏷️ ARTIKEL KÜTÜPHANESİ SEKMESİ ---
with sekme2:
    st.markdown("### 🏷️ Artikel Kaydet")
    y_ad = st.text_input("Artikel Numarası").upper()
    y_te = st.number_input("TE Değeri", format="%.3f", value=None)
    if st.button("Kütüphaneye Ekle"):
        if y_ad and y_te:
            st.session_state["kutuphane"][y_ad] = y_te
            st.success(f"{y_ad} başarıyla kaydedildi.")
            st.rerun()
