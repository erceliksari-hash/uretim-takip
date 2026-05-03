import streamlit as st
import pandas as pd
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Üretim Takip Pro v143", layout="wide")

# --- HTML/CSS İLE GÖRÜNÜMÜ İYİLEŞTİRME ---
# Bu kısım Python kodunu eski HTML stiline benzetir
st.markdown("""
    <style>
    /* Ana Arkaplan */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Kart Yapısı (HTML'deki .card gibi) */
    div[data-testid="stVerticalBlock"] > div {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 10px;
    }

    /* Giriş Kutuları */
    input {
        background-color: #0d1117 !important;
        color: white !important;
        border: 1px solid #30363d !important;
    }

    /* HTML Stili Yeşil Buton */
    div.stButton > button:first-child {
        background-color: #238636;
        color: white;
        border: 1px solid rgba(240,246,252,0.1);
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 600;
        width: 100%;
        transition: 0.2s;
    }
    
    div.stButton > button:first-child:hover {
        background-color: #2ea043;
        border-color: #8b949e;
    }

    /* Tablo Görünümü */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }
    
    /* Başlıklar */
    h1, h2, h3 {
        color: #58a6ff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ŞİFRE KONTROLÜ ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown("<h2 style='text-align: center;'>🔐 Üretim Portalı Girişi</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        sifre = st.text_input("Giriş Şifresi", type="password")
        if st.button("Giriş Yap"):
            if sifre == "1641":
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Hatalı Şifre!")
    st.stop()

# --- VERİ VE KÜTÜPHANE ---
if "liste" not in st.session_state:
    st.session_state["liste"] = []
if "kutuphane" not in st.session_state:
    st.session_state["kutuphane"] = {"PERÇİN": 0.550}

# --- YAN MENÜ ---
st.sidebar.markdown("### ⚙️ Menü")
sayfa = st.sidebar.radio("", ["🏠 Üretim Ekranı", "🏷️ Artikel Kütüphanesi", "📜 Günlük Arşiv"])

# --- 🏠 ÜRETİM EKRANI ---
if sayfa == "🏠 Üretim Ekranı":
    st.markdown("### 🚀 Günlük Üretim Girişi")
    
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            art_sec = st.selectbox("Artikel Seç", list(st.session_state["kutuphane"].keys()))
            adet = st.number_input("Adet", min_value=0, step=1)
            verim = st.number_input("Verim", value=1.0, step=0.1)
        with c2:
            rust = st.number_input("Rüst", min_value=0, step=1)
            gmk = st.number_input("GMK", min_value=0, step=1)
            notlar = st.text_input("Auftrag / Not")

        # Anlık Hesaplama Gösterimi
        te_deg = st.session_state["kutuphane"][art_sec]
        hesap_dk = (adet * te_deg) / verim
        toplam_dk = hesap_dk + rust + gmk
        st.markdown(f"<p style='color:#58a6ff; font-weight:bold;'>Hesaplanan: {toplam_dk:.2f} Dakika</p>", unsafe_allow_html=True)

        if st.button("LİSTEYE EKLE"):
            yeni = {
                "Zaman": datetime.now().strftime("%H:%M"),
                "Auftrag": notlar,
                "Artikel": art_sec,
                "Adet": adet,
                "Net DK": round(hesap_dk, 2),
                "Rüst": rust,
                "GMK": gmk,
                "Toplam": round(toplam_dk, 2)
            }
            st.session_state["liste"].append(yeni)
            st.rerun()

    # Üretim Tablosu
    if st.session_state["liste"]:
        st.markdown("### 📊 Bugünün Üretimi")
        df = pd.DataFrame(st.session_state["liste"])
        st.dataframe(df, use_container_width=True)
        
        # Özet Kartları
        t_dk = df["Toplam"].sum()
        fark = 465 - t_dk
        k1, k2 = st.columns(2)
        k1.metric("Toplam Süre", f"{t_dk:.2f} dk")
        k2.metric("Kalan Hedef", f"{fark:.2f} dk", delta=-fark, delta_color="inverse")

# --- Diğer sayfalar (Kütüphane ve Arşiv) aynı mantıkla devam eder ---
elif sayfa == "🏷️ Artikel Kütüphanesi":
    st.markdown("### 🏷️ Artikel Yönetimi")
    y_ad = st.text_input("Yeni Artikel Adı").upper()
    y_te = st.number_input("TE Değeri", format="%.3f")
    if st.button("KAYDET"):
        st.session_state["kutuphane"][y_ad] = y_te
        st.success("Kaydedildi!")
    
    st.write("---")
    st.table(pd.DataFrame(list(st.session_state["kutuphane"].items()), columns=["Artikel", "TE"]))

elif sayfa == "📜 Günlük Arşiv":
    st.markdown("### 📜 Arşiv")
    if st.session_state["liste"]:
        st.download_button("Excel Olarak İndir (CSV)", pd.DataFrame(st.session_state["liste"]).to_csv().encode('utf-8'), "uretim.csv")
        if st.button("Günü Sıfırla"):
            st.session_state["liste"] = []
            st.rerun()
