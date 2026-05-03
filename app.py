import streamlit as st
import pandas as pd
from datetime import datetime

# --- ŞİFRELEME ---
def giris_kontrol():
    if "giris_yapildi" not in st.session_state:
        st.session_state["giris_yapildi"] = False

    if not st.session_state["giris_yapildi"]:
        st.title("🔐 Üretim Takip Sistemi")
        sifre = st.text_input("Giriş Şifresi", type="password")
        if st.button("Giriş Yap"):
            if sifre == "percin123":  # ŞİFREN BURADA
                st.session_state["giris_yapildi"] = True
                st.rerun()
            else:
                st.error("Hatalı Şifre!")
        return False
    return True

if giris_kontrol():
    # --- ANA UYGULAMA ---
    st.sidebar.title("Menü")
    sayfa = st.sidebar.radio("Sayfa Seçin", ["🏠 Üretim Girişi", "🏷️ Artikel Kütüphanesi", "📜 Arşiv"])

    # Kütüphane (Basit bir örnek - Gerçekte bir dosyadan okunabilir)
    if "rehber" not in st.session_state:
        st.session_state["rehber"] = {"PERÇİN": 0.550, "CIVATA": 0.320}

    if sayfa == "🏠 Üretim Girişi":
        st.header("Günlük Üretim")
        secilen_art = st.selectbox("Artikel Seç", list(st.session_state["rehber"].keys()))
        te = st.session_state["rehber"][secilen_art]
        
        adet = st.number_input("Adet", min_value=0)
        verim = st.number_input("Verim", value=1.0)
        
        dk = (adet * te) / verim
        st.write(f"**Hesaplanan Dakika:** {dk:.2f}")

        if st.button("Listeye Ekle"):
            st.success(f"{secilen_art} listeye eklendi.")

    elif sayfa == "🏷️ Artikel Kütüphanesi":
        st.header("Kütüphane Oluştur")
        yeni_ad = st.text_input("Artikel Adı").upper()
        yeni_te = st.number_input("TE Değeri", format="%.3f")
        if st.button("Rehbere Kaydet"):
            st.session_state["rehber"][yeni_ad] = yeni_te
            st.success("Kütüphane güncellendi!")
        
        st.table(pd.DataFrame(st.session_state["rehber"].items(), columns=["Artikel", "TE"]))
