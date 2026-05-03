import streamlit as st
import pandas as pd
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Üretim Takip Pro v149", layout="wide")

# --- BEYAZ TEMA VE ÜST MENÜ STİLİ ---
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
        font-weight: 600;
        width: 100%;
        border: none;
        height: 45px;
    }
    h3 { color: #0969da !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ŞİFRE KONTROLÜ (SECRETS'TAN ÇEKİLİYOR) ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown("<h2 style='text-align: center;'>🔐 Üretim Portalı Girişi</h2>", unsafe_allow_html=True)
    c1, col_login, c3 = st.columns([1,1,1])
    with col_login:
        # Şifreyi Secrets'tan alıyoruz
        dogru_sifre = st.secrets["GIRIS_SIFRESI"]
        
        sifre_deneme = st.text_input("Giriş Şifresi", type="password", placeholder="Şifreyi yazınız...")
        if st.button("Giriş Yap"):
            if sifre_deneme == dogru_sifre:
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("❌ Hatalı Şifre!")
    st.stop()

# --- VERİ YAPISI ---
if "liste" not in st.session_state:
    st.session_state["liste"] = []
if "kutuphane" not in st.session_state:
    st.session_state["kutuphane"] = {}

# --- ÜST SEKMELİ MENÜ ---
sekme1, sekme2, sekme3 = st.tabs(["🏠 Üretim Girişi", "🏷️ Artikel Kütüphanesi", "📜 Günlük Arşiv"])

# --- 🏠 ÜRETİM GİRİŞİ SEKMESİ ---
with sekme1:
    st.markdown("### 🚀 Yeni İş Girişi")
    
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            kutuphane_listesi = list(st.session_state["kutuphane"].keys())
            art_sec = st.selectbox("Artikel Seç", [""] + kutuphane_listesi, index=0)
            adet = st.number_input("Adet", min_value=0, value=None, step=1, placeholder="Sayı giriniz...")
            verim = st.number_input("Verim", min_value=0.1, value=None, step=0.1, placeholder="Örn: 1.0")
        with c2:
            rust = st.number_input("Rüst (Dk)", min_value=0, value=None, step=1, placeholder="Sayı giriniz...")
            gmk = st.number_input("GMK (Dk)", min_value=0, value=None, step=1, placeholder="Sayı giriniz...")
            notlar = st.text_input("Auftrag / Not", value="", placeholder="İsteğe bağlı not...")

        toplam_dk = 0.0
        if art_sec != "" and adet is not None:
            te_deg = st.session_state["kutuphane"][art_sec]
            v_oran = verim if verim is not None else 1.0
            hesap_dk = (adet * te_deg) / v_oran
            r_ek = rust if rust is not None else 0
            g_ek = gmk if gmk is not None else 0
            toplam_dk = hesap_dk + r_ek + g_ek
            st.markdown(f"<p style='color:#0969da; font-weight:bold; font-size:20px;'>Hesaplanan: {toplam_dk:.2f} Dakika</p>", unsafe_allow_html=True)

        if st.button("LİSTEYE EKLE"):
            if art_sec == "" or adet is None:
                st.warning("Lütfen Artikel seçin ve Adet girin!")
            else:
                v_oran = verim if verim is not None else 1.0
                r_ek = rust if rust is not None else 0
                g_ek = gmk if gmk is not None else 0
                yeni = {
                    "Saat": datetime.now().strftime("%H:%M"),
                    "Auftrag": notlar,
                    "Artikel": art_sec,
                    "Adet": adet,
                    "Net DK": round((adet * st.session_state["kutuphane"][art_sec]) / v_oran, 2),
                    "Rüst": r_ek,
                    "GMK": g_ek,
                    "Toplam": round(toplam_dk, 2)
                }
                st.session_state["liste"].insert(0, yeni)
                st.rerun()

    if st.session_state["liste"]:
        st.markdown("### 📊 Bugünün Kayıtları")
        st.table(pd.DataFrame(st.session_state["liste"]))

# --- 🏷️ ARTIKEL KÜTÜPHANESİ SEKMESİ ---
with sekme2:
    st.markdown("### 🏷️ Yeni Artikel Tanımla")
    with st.container():
        y_ad = st.text_input("Artikel İsmi", value="", placeholder="İsim giriniz...").upper()
        y_te = st.number_input("TE Değeri (Dakika)", format="%.3f", value=None, placeholder="Örn: 0.550")
        if st.button("REHBERE KAYDET"):
            if y_ad and y_te is not None:
                st.session_state["kutuphane"][y_ad] = y_te
                st.success(f"{y_ad} kütüphaneye eklendi!")
                st.rerun()
            else:
                st.error("Lütfen isim ve TE değeri girin!")
    
    if st.session_state["kutuphane"]:
        st.write("---")
        st.table(pd.DataFrame(list(st.session_state["kutuphane"].items()), columns=["Artikel", "TE"]))

# --- 📜 GÜNLÜK ARŞİV SEKMESİ ---
with sekme3:
    st.markdown("### 📜 Arşiv")
    if st.session_state["liste"]:
        csv = pd.DataFrame(st.session_state["liste"]).to_csv(index=False).encode('utf-8')
        st.download_button("📥 Verileri İndir (Excel/CSV)", data=csv, file_name="uretim.csv")
        if st.button("🔴 LİSTEYE TEMİZLE"):
            st.session_state["liste"] = []
            st.rerun()
