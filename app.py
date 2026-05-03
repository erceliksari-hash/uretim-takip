import streamlit as st
import pandas as pd
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Üretim Takip Pro v150", layout="wide")

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
        border: none;
        border-radius: 6px;
    }
    .total-row {
        background-color: #e6f3ff !important;
        font-weight: bold;
    }
    h3 { color: #0969da !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ŞİFRE KONTROLÜ (SECRETS) ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown("<h2 style='text-align: center;'>🔐 Üretim Portalı Girişi</h2>", unsafe_allow_html=True)
    c1, col_login, c3 = st.columns([1,1,1])
    with col_login:
        dogru_sifre = st.secrets["GIRIS_SIFRESI"]
        s_input = st.text_input("Giriş Şifresi", type="password", placeholder="Şifreyi yazınız...")
        if st.button("Giriş Yap"):
            if s_input == dogru_sifre:
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

# --- ÜST MENÜ ---
sekme1, sekme2, sekme3 = st.tabs(["🏠 Üretim Girişi", "🏷️ Artikel Kütüphanesi", "📜 Günlük Arşiv"])

# --- 🏠 ÜRETİM GİRİŞİ SEKMESİ ---
with sekme1:
    st.markdown("### 🚀 Yeni İş Girişi")
    
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            kutuphane_listesi = list(st.session_state["kutuphane"].keys())
            art_sec = st.selectbox("Artikel Seç", [""] + kutuphane_listesi, index=0)
            adet = st.number_input("Adet", min_value=0, value=None, step=1, placeholder="Üretim miktarı...")
            verim = st.number_input("Verim", min_value=0.1, value=None, step=0.1, placeholder="Varsayılan: 1.0")
        with c2:
            rust = st.number_input("Rüst (Dk)", min_value=0, value=None, step=1, placeholder="Hazırlık süresi...")
            gmk = st.number_input("GMK (Dk)", min_value=0, value=None, step=1, placeholder="Ek süre...")
            notlar = st.text_input("Auftrag / Not", placeholder="Notunuzu buraya yazın...")

        # Formülleri Uygula (HTML v6 ile birebir aynı)
        toplam_is_dk = 0.0
        net_dk = 0.0
        if art_sec != "" and adet is not None:
            te_degeri = st.session_state["kutuphane"][art_sec]
            v_katsayi = verim if verim is not None else 1.0
            
            # Formül: (Adet * TE) / Verim
            net_dk = round((adet * te_degeri) / v_katsayi, 2)
            
            r_val = rust if rust is not None else 0
            g_val = gmk if gmk is not None else 0
            
            # Formül: Net Dk + Rüst + GMK
            toplam_is_dk = round(net_dk + r_val + g_val, 2)
            
            st.markdown(f"**Anlık Hesaplama:** {net_dk} (Net) + {r_val} (Rüst) + {g_val} (GMK) = **{toplam_is_dk} Dakika**")

        if st.button("LİSTEYE EKLE"):
            if art_sec == "" or adet is None:
                st.warning("Lütfen Artikel ve Adet bilgilerini eksiksiz girin!")
            else:
                yeni_kayit = {
                    "Saat": datetime.now().strftime("%H:%M"),
                    "Auftrag": notlar,
                    "Artikel": art_sec,
                    "Adet": adet,
                    "Net DK": net_dk,
                    "Rüst": rust if rust is not None else 0,
                    "GMK": gmk if gmk is not None else 0,
                    "Toplam": toplam_is_dk
                }
                st.session_state["liste"].insert(0, yeni_kayit)
                st.rerun()

    # --- TOPLAM LİSTE VE HESAPLAMALAR ---
    if st.session_state["liste"]:
        st.markdown("### 📊 Günlük Üretim Listesi")
        df = pd.DataFrame(st.session_state["liste"])
        
        # Tabloyu göster
        st.table(df)

        # DEĞERLERİ TOPLA (Genel Toplam Satırı)
        toplam_adet = df["Adet"].sum()
        toplam_net = df["Net DK"].sum()
        toplam_rust = df["Rüst"].sum()
        toplam_gmk = df["GMK"].sum()
        genel_toplam = df["Toplam"].sum()

        # Alt Toplam Paneli
        st.markdown("#### 🚩 Genel Toplamlar")
        t1, t2, t3, t4, t5 = st.columns(5)
        t1.metric("Toplam Adet", f"{toplam_adet:,}")
        t2.metric("Toplam Net DK", f"{toplam_net:.2f}")
        t3.metric("Toplam Rüst", f"{toplam_rust}")
        t4.metric("Toplam GMK", f"{toplam_gmk}")
        t5.metric("GENEL TOPLAM", f"{genel_toplam:.2f} dk", delta=f"{465-genel_toplam:.2f} dk fark")

# --- 🏷️ ARTIKEL KÜTÜPHANESİ ---
with sekme2:
    st.markdown("### 🏷️ Yeni Artikel Tanımla")
    y_ad = st.text_input("Artikel İsmi", key="new_art").upper()
    y_te = st.number_input("TE Değeri (Dakika)", format="%.3f", value=None, key="new_te")
    if st.button("REHBERE KAYDET"):
        if y_ad and y_te is not None:
            st.session_state["kutuphane"][y_ad] = y_te
            st.success(f"{y_ad} eklendi.")
            st.rerun()
    
    if st.session_state["kutuphane"]:
        st.write("---")
        st.table(pd.DataFrame(list(st.session_state["kutuphane"].items()), columns=["Artikel", "TE"]))

# --- 📜 GÜNLÜK ARŞİV ---
with sekme3:
    st.markdown("### 📜 Veri Yönetimi")
    if st.session_state["liste"]:
        st.download_button("📥 Excel/CSV Olarak İndir", data=pd.DataFrame(st.session_state["liste"]).to_csv(index=False).encode('utf-8'), file_name="uretim_ozet.csv")
        if st.button("🔴 TÜMÜNÜ SİL VE GÜNÜ BİTİR"):
            st.session_state["liste"] = []
            st.rerun()
