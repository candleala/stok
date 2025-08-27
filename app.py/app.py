import streamlit as st
import pandas as pd

st.set_page_config(page_title="Maça Stok Kontrol", layout="centered")
st.title("📦 Maça Stok Kontrol Paneli")

uploaded_file = st.file_uploader("CSV Dosyası Yükle", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=';')
    stok_input = st.text_input("Stok Kodu Gir", "")

    if stok_input:
        matches = df[df['STOK_KODU'].astype(str).str.contains(stok_input)]

        if not matches.empty:
            for _, row in matches.iterrows():
                buffer = row.get("BUFFER", "-")
                depo = row.get("DEPO", "-")
                pasif = row.get("PASIF", "-")
                st.markdown(f"""
**Stok Kodu:** {row['STOK_KODU']}  
- BUFFER: {buffer}  
- DEPO: {depo}  
- PASIF: {pasif}  
""")
        else:
            st.warning("Stok bulunamadı.")