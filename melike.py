import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import re
import unicodedata
import base64
import os

df_tahlil = pd.read_excel("dataset/melike-tahlil-merged_final.xlsx", index_col=False, sheet_name='Sheet1')
tests = df_tahlil.Tahlil.unique()
df_tahlil['Tarih'] = pd.to_datetime(df_tahlil['Tarih'], format='%d.%m.%Y %H:%M:%S')
df_tahlil['Tarih2'] = df_tahlil['Tarih'].dt.strftime('%Y-%m-%d')
df_tarih_sirali = df_tahlil.sort_values(by='Tarih2', ascending=True)

def clean_text(text):
    if isinstance(text, str):
        text = re.sub(r'[\x00-\x1F\x7F-\x9F\u200B-\u200D\uFEFF\u202C]+', '', text)
        text = unicodedata.normalize('NFKC', text)
    return text

df_tahlil['Tahlil'] = df_tahlil['Tahlil'].apply(clean_text)

st.title("Tahlil Verileri Grafik Sunumu")
st.subheader("Zamana Bağlı Değişim")

selected_test = st.selectbox("Bir tahlil seçin:", tests)

def draw_graph(tahlil):
    df = df_tarih_sirali.query("Tahlil == @tahlil")
    try:
        tahlil_adı = df.Tahlil.values[0]
        birim = df['Sonuç Birimi'].values[0]
        referans = df['Referans Değeri'].values[0]
        referans_parcalar = referans.split()
        if len(referans_parcalar) >= 3:
            referans_alt = float(referans_parcalar[0].replace(",", "."))
            referans_ust = float(referans_parcalar[2].replace(",", "."))
        else:
            referans_alt = referans_ust = None

        x = df.Tarih.values
        y = df.Sonuç.values

        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(x, y, marker='o', label='Sonuç')
        if referans_alt is not None and referans_ust is not None:
            ax.axhline(y=referans_alt, color='r', linestyle=':', label='Referans Alt')
            ax.axhline(y=referans_ust, color='r', linestyle=':', label='Referans Üst')
        ax.set_title(tahlil)
        ax.set_ylabel(f"{birim} ({referans})")
        # fig.autofmt_xdate()
        ax.set_xticks(x)
        ax.tick_params(axis='x', rotation=90, width=2)
        ax.legend()
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Grafik çizilemedi: {e}")

if selected_test:
    draw_graph(selected_test)

st.markdown("""
            ### Notlar: Hastanın genel seyri
            * Beyin Cerrahi Operasyon Tarihi 13 Ocak. Kemik metastazına bağlı olarak L3 omurunda fraktür.
            * Ameliyat öncesi Edinimli Hemofili A tanısı kondu.
            * Ameliyat sırasında kanı pıhtılaştırmak için Novo7 kullanıldı. Faktör 7.
            * Buan rağmen operasyon sonrası kanamaya bağlı olarak 14 Ocak'ta tekrar operasyona alındı.
            * Sonrasında omiriliğine gelen kanama basısı neticesinde 2 diz altı kısmı hafif felç oldu. 
            * Fizik tedaviye başlandı. Yanıt verdi.
            * Hastalanmadan önce yürüteç desteği ile kendi başına yürüyebiliyordu.
            * WBC ve bazı değer bir anda ani sapma gösteriyor.
            * Radyoterapi başlangıç tarihi 16 Mayıs. 10 Seans. Bitiş tarihi 2 Mayıs Cuma.
            * Tümör belirteçlerinde gerileme var. (CA 19-9, CEA)
            * Son Acil US raporunda: Klinik Bilgi:HASTANIN INSZIYON HATTINA APSE? TDRO; 
            """)

# Belge görüntüleme bölümü (PDF + Görsel)
st.header("Belge Görüntüleyici (PDF / Görsel)")

allowed_extensions = ('.pdf', '.jpg', '.jpeg', '.png')
document_files = [f for f in os.listdir("documents") if f.lower().endswith(allowed_extensions)]

if document_files:
    selected_file = st.selectbox("Bir dosya seçin:", document_files)
    file_path = os.path.join("documents", selected_file)

    if selected_file.lower().endswith(".pdf"):
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="900" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
            # İndirme düğmesi
            st.download_button(
                label="PDF dosyasını indir",
                data=f,
                file_name=selected_file,
                mime="application/pdf"
            )
    else:
        st.image(file_path, caption=selected_file, use_container_width=True)
        # İndirme düğmesi
        with open(file_path, "rb") as f:
            st.download_button(
                label="Görsel dosyasını indir",
                data=f,
                file_name=selected_file,
                mime="image/jpeg" if selected_file.lower().endswith(('.jpg', '.jpeg')) else "image/png"
            )
else:
    st.info("Documents klasöründe PDF veya görsel dosyası bulunamadı.")
