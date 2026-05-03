import streamlit as st
import pandas as pd
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Üretim Takip Pro v147", layout="wide")

# --- BEYAZ TEMA VE ÜST MENÜ STİLİ ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1f2328; }
    [data-testid="stSidebar"] { display: none; }
    
    /* Giriş Kutuları ve Kart Tasarımı */
    div[data-testid="stVerticalBlock"] > div {
        background-color: #f6f8fa;
        border: 1px solid #d0d7de;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 10px;
    }

    /* Tablo Tasarımı */
    .stTable { background-color: white; border-radius: 10px; }

    /* Yeşil Ekleme Butonu */
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

# --- ŞİFRE KONTROLÜ (1641) ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown("<h2 style='text-align: center;'>🔐 Üretim Portalı Girişi</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        sifre = st.text_input("Giriş Şifresi", type="password")
        if st.button("Giriş Yap"):
            if sifre == "1641":
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Hatalı Şifre!")
    st.stop()

# --- TAMAMEN BOŞ VERİ YAPISI ---
if "liste" not in st.session_state:
    st.session_state["liste"] = []
if "kutuphane" not in st.session_state:
    # Tüm kayıtlı artikelleri (Perçin dahil) sildik, liste boş başlıyor.
    st.session_state["kutuphane"] = {}

# --- ÜST SEKMELİ MENÜ ---
sekme1, sekme2, sekme3 = st.tabs(["🏠 Üretim Girişi", "🏷️ Artikel Kütüphanesi", "📜 Günlük Arşiv"])

# --- 🏠 ÜRETİM GİRİŞİ SEKMESİ ---
with sekme1:
    st.markdown("### 🚀 Yeni İş Girişi")
    
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            # Artikel seçimi boş başlıyor
            kutuphane_listesi = list(st.session_state["kutuphane"].keys())
            art_sec = st.selectbox("Artikel Seç", [""] + kutuphane_listesi, index=0)
            adet = st.number_input("Adet", min_value=0, value=0, step=1)
            verim = st.number_input("Verim", min_value=0.1, value=1.0, step=0.1)
        with c2:
            rust = st.number_input("Rüst (Dk)", min_value=0, value=0, step=1)
            gmk = st.number_input("GMK (Dk)", min_value=0, value=0, step=1)
            notlar = st.text_input("Auftrag / Not", value="")

        # Hesaplama Mantığı
        toplam_dk = 0.0
        if art_sec != "" and art_sec in st.session_state["kutuphane"]:
            te_deg = st.session_state["kutuphane"][art_sec]
            hesap_dk = (adet * te_deg) / verim
            toplam_dk = hesap_dk + rust + gmk
            st.markdown(f"<p style='color:#0969da; font-weight:bold; font-size:20px;'>Hesaplanan: {toplam_dk:.2f} Dakika</p>", unsafe_allow_html=True)

        if st.button("LİSTEYE EKLE"):
            if art_sec == "":
                st.warning("Lütfen önce Kütüphane sekmesinden bir Artikel tanımlayın ve seçin!")
            else:
                yeni = {
                    "Saat": datetime.now().strftime("%H:%M"),
                    "Auftrag": notlar,
                    "Artikel": art_sec,
                    "Adet": adet,
                    "Net DK": round((adet * st.session_state["kutuphane"][art_sec]) / verim, 2),
                    "Rüst": rust,
                    "GMK": gmk,
                    "Toplam": round(toplam_dk, 2)
                }
                st.session_state["liste"].insert(0, yeni)
                st.rerun()

    if st.session_state["liste"]:
        st.markdown("### 📊 Bugünün Kayıtları")
        df = pd.DataFrame(st.session_state["liste"])
        st.table(df)
        
        t_dk = df["Toplam"].sum()
        fark = 465 - t_dk
        k1, k2 = st.columns(2)
        k1.metric("Toplam Üretim", f"{t_dk:.2f} dk")
        k2.metric("Kalan Hedef", f"{fark:.2f} dk", delta=-fark, delta_color="inverse")

# --- 🏷️ ARTIKEL KÜTÜPHANESİ SEKMESİ ---
with sekme2:
    st.markdown("### 🏷️ Yeni Artikel Tanımla")
    with st.container():
        # Giriş alanları boş (temiz) geliyor
        y_ad = st.text_input("Artikel İsmi", value="").upper()
        # TE değeri 0.000 olarak boş (sıfırlanmış) geliyor
        y_te = st.number_input("TE Değeri (Dakika)", format="%.3f", value=0.000)
        
        if st.button("REHBERE KAYDET"):
            if y_ad and y_te > 0:
                st.session_state["kutuphane"][y_ad] = y_te
                st.success(f"{y_ad} kütüphaneye eklendi!")
                st.rerun()
            else:
                st.error("Lütfen Artikel ismi ve geçerli bir TE değeri girin!")
    
    st.write("---")
    st.markdown("### 📖 Kayıtlı Artikeller")
    if st.session_state["kutuphane"]:
        st.table(pd.DataFrame(list(st.session_state["kutuphane"].items()), columns=["Artikel", "TE"]))
    else:
        st.info("Kütüphane şu an boş. Lütfen yukarıdan yeni bir Artikel ekleyin.")

# --- 📜 GÜNLÜK ARŞİV SEKMESİ ---
with sekme3:
    st.markdown("### 📜 Gün Sonu ve Arşiv")
    if st.session_state["liste"]:
        csv = pd.DataFrame(st.session_state["liste"]).to_csv(index=False).encode('utf-8')
        st.download_button("📥 Verileri İndir (Excel/CSV)", data=csv, file_name=f"uretim_{datetime.now().strftime('%d_%m')}.csv")
        
        if st.button("🔴 TÜM LİSTEYİ TEMİZLE"):
            st.session_state["liste"] = []
            st.rerun()
    else:
        st.info("Henüz kaydedilmiş bir üretim bulunmuyor.")
