import streamlit as st
import pandas as pd
from datetime import datetime

# --- SAYFA AYARLARI (Mobil Uyumlu) ---
st.set_page_config(page_title="Üretim Takip Pro v154", layout="wide")

# --- CSS TASARIMI (Mobil ve Tablet Öncelikli) ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1f2328; }
    [data-testid="stSidebar"] { display: none; }
    
    /* Kart yapısı */
    div[data-testid="stVerticalBlock"] > div {
        background-color: #f6f8fa;
        border: 1px solid #d0d7de;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    
    /* Buton Tasarımları */
    .stButton > button {
        width: 100% !important;
        height: 50px;
        border-radius: 8px;
        font-weight: bold;
    }
    .main-btn > div > button { background-color: #1f883d !important; color: white !important; }
    .archive-btn > div > button { background-color: #0969da !important; color: white !important; }
    .delete-btn > div > button { background-color: #cf222e !important; color: white !important; }
    
    /* Tablo font küçültme (Mobilde taşmaması için) */
    .stTable { font-size: 12px !important; }
    
    h3 { color: #0969da !important; font-size: 1.2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ YAPISI VE OTURUM YÖNETİMİ ---
if "liste" not in st.session_state:
    st.session_state["liste"] = []
if "arsiv" not in st.session_state:
    st.session_state["arsiv"] = []
if "kutuphane" not in st.session_state:
    st.session_state["kutuphane"] = {}
if "form_key" not in st.session_state:
    st.session_state["form_key"] = 0

def form_sifirla():
    st.session_state["form_key"] += 1

# --- ÜST MENÜ ---
sekme1, sekme2, sekme3 = st.tabs(["🏠 Üretim Girişi", "🏷️ Artikel Kütüphanesi", "📜 Günlük Arşiv"])

# --- 🏠 ÜRETİM GİRİŞİ SEKMESİ ---
with sekme1:
    st.markdown("### 🚀 Yeni İş Girişi")
    
    with st.container():
        art_sec = st.selectbox("Artikel Numarası", [""] + list(st.session_state["kutuphane"].keys()), 
                               index=0, key=f"art_{st.session_state['form_key']}")
        
        col1, col2 = st.columns(2) # Mobilde yan yana gelmesi için 2'li bölme
        with col1:
            adet = st.number_input("Adet (STK)", min_value=0, value=None, key=f"adet_{st.session_state['form_key']}")
            # TE Girişi (Tam sayı göstermek için format)
            varsayilan_te = st.session_state["kutuphane"].get(art_sec, None) if art_sec != "" else None
            te_giris = st.number_input("TE Değeri", format="%.3f", value=varsayilan_te, key=f"te_{st.session_state['form_key']}")
        
        with col2:
            verim = st.number_input("Veri Prosent", min_value=0.1, value=None, key=f"ver_{st.session_state['form_key']}")
            rust = st.number_input("Rüst (Dk)", min_value=0, value=None, key=f"rust_{st.session_state['form_key']}")

        gmk = st.number_input("GMK (Dk)", min_value=0, value=None, key=f"gmk_{st.session_state['form_key']}")
        notlar = st.text_input("Not / Auftrag", key=f"not_{st.session_state['form_key']}")

        toplam_is_dk = 0.0
        if adet is not None and te_giris is not None:
            v_oran = verim if verim is not None else 1.0
            net_dk = (adet * te_giris) / v_oran
            toplam_is_dk = round(net_dk + (rust or 0) + (gmk or 0), 2)
            st.info(f"Hesaplanan: {toplam_is_dk} dk")

        st.markdown('<div class="main-btn">', unsafe_allow_html=True)
        if st.button("LİSTEYE EKLE"):
            if adet is None or te_giris is None:
                st.warning("Eksik bilgi!")
            else:
                yeni = {
                    "Tarih": datetime.now().strftime("%Y-%m-%d"),
                    "Artikel No": art_sec if art_sec != "" else "Manuel",
                    "Adet": int(adet),
                    "TE": round(te_giris, 1), # Son iki basamağı gizlemek için yuvarlama (veya int)
                    "Verim": int(verim) if verim else 1,
                    "Rüst": rust or 0,
                    "GMK": gmk or 0,
                    "Toplam": toplam_is_dk,
                    "Not": notlar
                }
                st.session_state["liste"].insert(0, yeni)
                form_sifirla()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- LİSTE VE HESAPLAR ---
    if st.session_state["liste"]:
        st.markdown("### 📊 Günlük Liste")
        df = pd.DataFrame(st.session_state["liste"])
        st.table(df)

        # Yerleri Değiştirilmiş Toplam Kutuları
        st.write("---")
        col_kalan, col_toplam = st.columns(2)
        toplam_biriken = df["Toplam"].sum()
        
        with col_kalan:
            hedef = st.number_input("Hedef", value=465)
            st.metric("KALAN", f"{hedef - toplam_biriken:.2f}")
            
        with col_toplam:
            st.write("") # Hizalama için
            st.metric("ŞU ANKİ TOPLAM", f"{toplam_biriken:.2f}")

        # Aksiyon Butonları
        st.write("---")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="archive-btn">', unsafe_allow_html=True)
            if st.button("GÜNÜ ARŞİVLE VE TEMİZLE"):
                st.session_state["arsiv"].extend(st.session_state["liste"])
                st.session_state["liste"] = []
                st.success("Veriler arşive taşındı!")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
            if st.button("LİSTEYİ SİL"):
                st.session_state["liste"] = []
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- 🏷️ ARTIKEL KÜTÜPHANESİ ---
with sekme2:
    st.markdown("### 🏷️ Artikel Kaydet")
    y_ad = st.text_input("Artikel No").upper()
    y_te = st.number_input("Standart TE", format="%.3f", value=None)
    if st.button("Kaydet"):
        if y_ad and y_te:
            st.session_state["kutuphane"][y_ad] = y_te
            st.rerun()

# --- 📜 GÜNLÜK ARŞİV SEKMESİ (Arama Özellikli) ---
with sekme3:
    st.markdown("### 🔍 Arşivde Ara")
    if st.session_state["arsiv"]:
        arsiv_df = pd.DataFrame(st.session_state["arsiv"])
        
        # Tarih Filtresi
        secilen_tarih = st.date_input("Tarih Seçiniz", value=datetime.now())
        tarih_str = secilen_tarih.strftime("%Y-%m-%d")
        
        filtreli_df = arsiv_df[arsiv_df["Tarih"] == tarih_str]
        
        if not filtreli_df.empty:
            st.write(f"📅 {tarih_str} Tarihli Kayıtlar")
            st.table(filtreli_df)
            st.metric("O Günün Toplamı", f"{filtreli_df['Toplam'].sum():.2f}")
        else:
            st.warning("Bu tarihe ait kayıt bulunamadı.")
            
        if st.button("Tüm Arşivi Göster"):
            st.table(arsiv_df)
    else:
        st.info("Henüz arşivlenmiş veri yok.")
