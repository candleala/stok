import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import pytz

# -------------------------------
# Sayfa ayarları
# -------------------------------
st.set_page_config(page_title="MODEL RAFİNASYON ÇALIŞMASI", layout="wide")
st.title("MODEL RAFİNASYON ÇALIŞMASI")

# -------------------------------
# Kullanıcı adı girişi
# -------------------------------
user_name = st.text_input("Kullanıcı Adı")
if not user_name:
    st.warning("Lütfen kullanıcı adınızı girin.")
    st.stop()
else:
    st.success(f"Hoş geldiniz, {user_name}")

# -------------------------------
# Veritabanı bağlantısı
# -------------------------------
conn = sqlite3.connect("sorgular.db", check_same_thread=False)
c = conn.cursor()

# Tabloyu oluştur (ilk defa çalıştırıldığında)
c.execute('''
    CREATE TABLE IF NOT EXISTS sorgular (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kullanici TEXT,
        stok_kodu TEXT,
        buffer TEXT,
        depo TEXT,
        pasif TEXT,
        durum TEXT,
        tarih TEXT
    )
''')
conn.commit()

# -------------------------------
# CSV verisi gömülü
# -------------------------------
try:
    df = pd.read_csv("stoksorgulama.csv", sep=";", dtype=str)
    df.columns = [c.strip().upper().replace(" ", "_") for c in df.columns]
    for col in ['BUFFER', 'DEPO', 'PASIF']:
        if col not in df.columns:
            df[col] = "-"
    df = df.fillna("-")
except Exception as e:
    st.error(f"CSV okunurken hata oluştu: {e}")
    st.stop()

# -------------------------------
# Stok Kodu arama
# -------------------------------
stok_input = st.text_input("Stok Kodu Gir", placeholder="Örn: 79452-100 veya 79452")

if stok_input:
    matches = df[df['STOK_KODU'].str.contains(stok_input)]
    if not matches.empty:
        for _, row in matches.iterrows():
            buffer_val = row.get('BUFFER', "-").strip() or "-"
            depo_val = row.get('DEPO', "-").strip() or "-"
            pasif_val = row.get('PASIF', "-").strip() or "-"

            # Renk belirleme: BUFFER > DEPO > PASIF
            if buffer_val != "-":
                bg_color = "#4CAF50"  # yeşil
                text_color = "white"
            elif depo_val != "-":
                bg_color = "#FFD700"  # sarı
                text_color = "black"
            elif pasif_val != "-":
                bg_color = "#F44336"  # kırmızı
                text_color = "white"
            else:
                bg_color = "#808080"  # gri
                text_color = "white"

            # Kart gösterimi
            lines = [
                f"Stok Kodu: {row['STOK_KODU']}",
                f"BUFFER: {buffer_val}",
                f"DEPO: {depo_val}",
                f"PASIF: {pasif_val}"
            ]

            st.markdown(
                f"<div style='background-color:{bg_color}; color:{text_color}; padding:15px; border-radius:8px; margin-bottom:12px; font-weight:bold; white-space:pre-line;'>{chr(10).join(lines)}</div>",
                unsafe_allow_html=True
            )

            # -------------------------------
            # Durum seçimi
            # -------------------------------
            durum_secim = st.radio(
                "Durum Seçin (zorunlu)",
                ["Maça etiketlendi", "Model etiketlendi", "Maça sandığı depoya transfer edildi",
                 "Model alt-üst şekilde depoya transfer edildi", "Maça ve model eşleştirildi", "Görüntülendi"],
                key=row['STOK_KODU']
            )

            if st.button("Kaydet", key="kaydet_"+row['STOK_KODU']):
                # İstanbul saati
                ist = pytz.timezone('Europe/Istanbul')
                tarih = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")

                try:
                    c.execute('''
                        INSERT INTO sorgular (kullanici, stok_kodu, buffer, depo, pasif, durum, tarih)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (user_name, row['STOK_KODU'], buffer_val, depo_val, pasif_val, durum_secim, tarih))
                    conn.commit()
                    st.success(f"{row['STOK_KODU']} başarıyla kaydedildi.")
                except Exception as e:
                    st.error(f"Veritabanına kaydedilirken hata oluştu: {e}")
    else:
        st.warning("Stok bulunamadı.")

# -------------------------------
# Geçmiş sorgular
# -------------------------------
st.subheader("Geçmiş Sorgular")
try:
    past = pd.read_sql_query("SELECT * FROM sorgular ORDER BY id DESC", conn)
    if not past.empty:
        st.dataframe(past)
    else:
        st.info("Henüz geçmiş sorgu yok.")
except Exception as e:
    st.error(f"Geçmiş sorgular okunamadı: {e}")
