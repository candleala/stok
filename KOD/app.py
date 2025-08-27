import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import pytz

# İstanbul saat dilimi
istanbul = pytz.timezone('Europe/Istanbul')

# Veritabanı bağlantısı ve tablo oluşturma
conn = sqlite3.connect("sorgular.db", check_same_thread=False)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS sorgular (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    stok_kodu TEXT,
    buffer TEXT,
    depo TEXT,
    pasif TEXT,
    durum TEXT,
    tarih TEXT
)
''')
conn.commit()

# Sayfa başlığı
st.set_page_config(page_title="MODEL RAFİNASYON ÇALIŞMASI", layout="wide")
st.title("MODEL RAFİNASYON ÇALIŞMASI")

# Kullanıcı adı girişi
user_name = st.text_input("Kullanıcı Adı")
if not user_name:
    st.warning("Lütfen kullanıcı adınızı girin.")
    st.stop()
st.success(f"Hoş geldiniz, {user_name}")

# CSV yükleme
uploaded_file = st.file_uploader("CSV Dosyasını Seçin (noktalı virgül ile)", type="csv")
stok_input = st.text_input("Stok Kodu Gir")

# Durum seçenekleri
durum_options = [
    "Maça etiketlendi",
    "Model etiketlendi",
    "Maça sandığı depoya transfer edildi",
    "Model alt-üst şekilde depoya transfer edildi",
    "Maça ve model eşleştirildi",
    "Görüntülendi"
]

if uploaded_file:
    try:
        # CSV'yi oku
        df = pd.read_csv(uploaded_file, sep=";", dtype=str)
        df.columns = [c.strip().upper().replace(" ", "_") for c in df.columns]
        for col in ['BUFFER','DEPO','PASIF']:
            if col not in df.columns:
                df[col] = "-"
        df = df.fillna("-")

        if stok_input:
            matches = df[df['STOK_KODU'].str.contains(stok_input, na=False)]
            if not matches.empty:
                for _, row in matches.iterrows():
                    buffer_val = row.get('BUFFER', "-") or "-"
                    depo_val = row.get('DEPO', "-") or "-"
                    pasif_val = row.get('PASIF', "-") or "-"

                    # Renk belirleme
                    if buffer_val != "-":
                        bg_color = "#4CAF50"; text_color="white"
                    elif depo_val != "-":
                        bg_color = "#FFD700"; text_color="black"
                    elif pasif_val != "-":
                        bg_color = "#F44336"; text_color="white"
                    else:
                        bg_color = "#808080"; text_color="white"

                    # Kart göster
                    st.markdown(
                        f"<div style='background:{bg_color}; color:{text_color}; padding:15px; border-radius:8px; margin-bottom:12px; font-weight:bold; white-space:pre-line;'>"
                        f"Stok Kodu: {row['STOK_KODU']}\nBUFFER: {buffer_val}\nDEPO: {depo_val}\nPASIF: {pasif_val}</div>",
                        unsafe_allow_html=True
                    )

                    # Durum seçimi ve kaydetme butonu
                    selected_durum = st.selectbox(f"Durum Seçin (zorunlu) - {row['STOK_KODU']}", durum_options)
                    if st.button(f"Kaydet - {row['STOK_KODU']}"):
                        now = datetime.now(istanbul).strftime("%Y-%m-%d %H:%M:%S")
                        c.execute('''
                            INSERT INTO sorgular (user, stok_kodu, buffer, depo, pasif, durum, tarih)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (user_name, row['STOK_KODU'], buffer_val, depo_val, pasif_val, selected_durum, now))
                        conn.commit()
                        st.success("Kayıt başarıyla eklendi!")

            else:
                st.warning("Stok bulunamadı.")

    except Exception as e:
        st.error(f"CSV okunurken hata oluştu: {e}")

# Geçmiş sorgular
st.subheader("Geçmiş Sorgular")
try:
    past = pd.read_sql_query("SELECT * FROM sorgular ORDER BY id DESC", conn)
    st.dataframe(past)
except Exception as e:
    st.error(f"Geçmiş sorgular okunamadı: {e}")
