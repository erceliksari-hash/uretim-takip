import streamlit as st
import pandas as pd
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Üretim Takip Pro v142", layout="wide", initial_sidebar_state="expanded")

# --- ŞİFRE AYARI ---
GIZLI_SIFRE = "1641"

# --- CSS: KOYU TEMA VE BUTONLAR ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    div.stButton > button:first-child { 
        background-color: #238636; 
        color: white; 
        border-radius: 8px; 
        border: none;
        padding: 10px;
        font-weight: bold;
    }
    .main-header { color: #58a6ff; text-align: center; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- GİRİŞ KONTROLÜ ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown('<p class="main-header">🔐 Üretim Takip Sistemi</p>', unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            sifre_input = st.text_input("Giriş Şifresi", type="password", placeholder="Şifreyi yazın...")
            if st.button("Sisteme Giriş Yap"):
                if sifre_input == GIZLI_SIFRE:
                    st.session_state["auth"] = True
                    st.rerun()
                else:
                    st.error("❌ Hatalı Şifre! Lütfen tekrar deneyin.")
    st.stop()

# --- VERİ DEPOLAMA (SESSION STATE) ---
if "liste" not in st.session_state:
    st.session_state["liste"] = []
if "kutuphane" not in st.session_state:
    # Başlangıç Kütüphanesi
    st.session_state["kutuphane"] = {"PERÇİN": 0.550, "CIVATA": 0.320}

# --- YAN MENÜ ---
with st.sidebar:
    st.title("📱 Menü")
    sayfa = st.radio("Gitmek istediğiniz sayfa:", ["🏠 Üretim Girişi", "🏷️ Artikel Rehberi", "📜 Günlük Özet"])
    st.divider()
    if st.button("🚪 Çıkış Yap"):
        st.session_state["auth"] = False
        st.rerun()

# --- 🏠 ÜRETİM GİRİŞİ ---
if sayfa == "🏠 Üretim Girişi":
    st.markdown('<p class="main-header">🏠 Günlük Üretim Girişi</p>', unsafe_allow_html=True)
    
    with st.form("uretim_formu", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            artikel = st.selectbox("Artikel Seçin", list(st.session_state["kutuphane"].keys()))
            adet = st.number_input("Üretilen Adet", min_value=0, step=1)
            verim = st.number_input("Verim (Boşsa 1 kabul edilir)", min_value=0.1, value=1.0, step=0.1)
        
        with col2:
            rust = st.number_input("Rüst (Dakika)", min_value=0, step=1)
            gmk = st.number_input("GMK (Dakika)", min_value=0, step=1)
            notlar = st.text_input("Auftrag / Not")
        
        ekle = st.form_submit_button("➕ LİSTEYE EKLE")

    if ekle:
        te = st.session_state["kutuphane"][artikel]
        hesaplanan_dk = (adet * te) / verim
        toplam = hesaplanan_dk + rust + gmk
        
        yeni_kayit = {
            "Zaman": datetime.now().strftime("%H:%M"),
            "Auftrag": notlar,
            "Artikel": artikel,
            "Adet": adet,
            "TE": te,
            "Net DK": round(hesaplanan_dk, 2),
            "Rüst": rust,
            "GMK": gmk,
            "Toplam": round(toplam, 2)
        }
        st.session_state["liste"].append(yeni_is)
        st.success(f"{artikel} başarıyla listeye eklendi!")

    # Tablo Gösterimi
    if st.session_state["liste"]:
        df = pd.DataFrame(st.session_state["liste"])
        st.table(df)
        
        # Hesaplamalar
        toplam_sure = df["Toplam"].sum()
        hedef = 465 # Standart hedef
        fark = hedef - toplam_sure
        
        c1, c2 = st.columns(2)
        c1.metric("Toplam Üretilen (DK)", f"{toplam_sure:.2f}")
        c2.metric("Kalan Hedef (Fark)", f"{fark:.2f}", delta=-fark, delta_color="inverse")

# --- 🏷️ ARTIKEL REHBERİ ---
elif sayfa == "🏷️ Artikel Rehberi":
    st.markdown('<p class="main-header">🏷️ Artikel & Kütüphane Yönetimi</p>', unsafe_allow_html=True)
    
    with st.expander("➕ Yeni Artikel Ekle"):
        yeni_ad = st.text_input("Artikel İsmi").upper()
        yeni_te = st.number_input("TE Değeri (Dakika)", format="%.3f")
        if st.button("Rehbere Kaydet"):
            if yeni_ad:
                st.session_state["kutuphane"][yeni_ad] = yeni_te
                st.success(f"{yeni_ad} rehbere eklendi!")
                st.rerun()
    
    st.subheader("Kayıtlı Artikeller")
    rehber_df = pd.DataFrame(list(st.session_state["kutuphane"].items()), columns=["Artikel", "TE"])
    st.dataframe(rehber_df, use_container_width=True)

# --- 📜 GÜNLÜK ÖZET ---
elif sayfa == "📜 Günlük Özet":
    st.markdown('<p class="main-header">📜 Günlük Özet ve Arşiv</p>', unsafe_allow_html=True)
    if st.session_state["liste"]:
        df_final = pd.DataFrame(st.session_state["liste"])
        st.dataframe(df_final, use_container_width=True)
        
        csv = df_final.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Günlük Veriyi Excel (CSV) İndir", data=csv, file_name=f"uretim_{datetime.now().strftime('%Y-%m-%d')}.csv")
        
        if st.button("🔴 GÜNÜ BİTİR (Tümünü Sil)"):
            st.session_state["liste"] = []
            st.warning("Tüm günlük veriler temizlendi.")
            st.rerun()
    else:
        st.info("Henüz kayıtlı veri bulunmuyor.")
