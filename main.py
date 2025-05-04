import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Create a folder for figures if it doesn't exist
os.makedirs("figures", exist_ok=True)

# Styling
colors = ['skyblue', 'plum']
plt.style.use('seaborn-v0_8')

# Veriyi yükle
df = pd.read_csv("dataset/2025salonfinal.csv")

st.title("2025 Salon Finali Sonuç Analizi")
st.markdown("""
Bu gösterge paneli, 2025 Salon Finali spor müsabakası sonuçlarının genel bir görünümünü ve analizini sunar.
Veriyi filtreleyebilir, özet istatistikleri görebilir ve görselleştirmelerle içgörüler elde edebilirsiniz.
""")

#################################################################################
# Kenar çubuğu filtreleri
st.sidebar.header("Veriyi Filtrele")
cities = st.sidebar.multiselect("İl Seçiniz", options=df["İL"].unique(), default=df["İL"].unique())
categories = st.sidebar.multiselect("Kategori Seçiniz", options=df["KATEGORİ"].unique(), default=df["KATEGORİ"].unique())

filtered_df = df[(df["İL"].isin(cities)) & (df["KATEGORİ"].isin(categories))]
#################################################################################
st.divider()
#################################################################################
# Veri Önizlemesi
st.subheader("Veri Önizlemesi")
st.dataframe(filtered_df)
st.divider()

# # Özet İstatistikler
# st.subheader("Özet İstatistikler")
# st.write(filtered_df[["HALKAPUANI", "İSABET", "TOPLAM"]].describe())
# st.divider()

#################################################################################
# Görselleştirmeler
st.subheader("Görselleştirmeler")

#################################################################################
# Yarışmaya katılanlar ve katılmayanların sayısı
st.markdown("**Yarışmaya Katılanlar ve Katılmayanlar**")

# Katılım durumunu belirle (TOPLAM puanı 0'dan büyük olanlar katılmış sayılır)
participants = len(filtered_df[filtered_df["TOPLAM"] > 0])
non_participants = len(filtered_df[filtered_df["TOPLAM"] == 0])

# Pie chart için veri hazırla
participation_data = [participants, non_participants]
labels = ['Katılanlar', 'Katılmayanlar']

# Pie chart oluştur
fig_part, ax_part = plt.subplots(figsize=(4, 4))
ax_part.pie(participation_data, labels=labels, autopct='%1.1f%%', colors=colors)
ax_part.set_title("Yarışmaya Katılım Oranı")

fig_part.savefig("figures/participation_pie.png", bbox_inches="tight")
st.pyplot(fig_part)
st.divider()
#################################################################################
# Katılımcı Sayısı: Her şehirden kaç sporcu katılmış ve katılmamış?
st.subheader("Şehirlere Göre Katılımcı Sayısı")
# Katılanlar ve katılmayanları hesapla
participants_by_city = df[df["TOPLAM"] > 0]["İL"].value_counts()
non_participants_by_city = df[df["TOPLAM"] == 0]["İL"].value_counts()

# Tüm şehirleri al
all_cities = df["İL"].unique()

# Eksik değerleri 0 ile doldur
participants_by_city = participants_by_city.reindex(all_cities, fill_value=0)
non_participants_by_city = non_participants_by_city.reindex(all_cities, fill_value=0)

# Veriyi DataFrame'e dönüştür
participation_df = pd.DataFrame({
    'Katılanlar': participants_by_city,
    'Katılmayanlar': non_participants_by_city
})

# Toplam katılımcı sayısına göre sırala
participation_df['Toplam'] = participation_df['Katılanlar'] + participation_df['Katılmayanlar']
participation_df = participation_df.sort_values('Toplam', ascending=False)
participation_df = participation_df.drop('Toplam', axis=1)

# Stack bar chart oluştur
fig0, ax0 = plt.subplots(figsize=(16, 8))
participation_df.plot(kind='bar', stacked=True, ax=ax0, color=colors, width=0.8)

ax0.set_ylabel("Sporcu Sayısı")
ax0.set_xlabel("İl")
ax0.set_title("Her Şehirden Katılan ve Katılmayan Sporcu Sayısı", fontsize='medium')
ax0.set_xticklabels(participation_df.index, rotation='vertical', ha="right", fontsize='medium')

# Toplam sayıları göster
for c in ax0.containers:
    ax0.bar_label(c, label_type='center')

# Gösterge etiketini düzenle
ax0.legend(title="Katılım Durumu")

fig0.savefig("figures/city_participation.png", bbox_inches="tight")
st.pyplot(fig0)

#################################################################################
# Detaylı veriyi tablo olarak göster
st.dataframe(participation_df)
st.divider()
#################################################################################
# 1b. Şehre Göre Toplam Puan Box-and-Whisker Grafiği
st.subheader("**Şehre Göre Ortalama Puan Dağılım Grafiği**")
fig1b, ax1b = plt.subplots(figsize=(16, 8))
# Sadece 0'dan büyük puanlar
box_data = filtered_df[filtered_df["TOPLAM"] > 0]
sns.boxplot(x="İL", y="TOPLAM", data=box_data, ax=ax1b, hue='İL', palette='tab20', legend=False)
ax1b.set_ylabel("Toplam Puan")
ax1b.set_xlabel("İl")
# Get current ticks and labels
ticks = ax1b.get_xticks()
labels = [label.get_text() for label in ax1b.get_xticklabels()]
# Set ticks and labels explicitly
ax1b.set_xticks(ticks)
ax1b.set_xticklabels(labels, rotation='vertical', ha="right")

fig1b.savefig("figures/boxplot_city.png", bbox_inches="tight")
st.pyplot(fig1b)
st.divider()

#################################################################################
# 2. Kategoriye Göre Puan Dağılımı
st.subheader("**Kategoriye Göre Puan Dağılımı**")
fig2, ax2 = plt.subplots(figsize=(16, 8))
box_data = filtered_df[filtered_df["TOPLAM"] > 0]
sns.boxplot(x="KATEGORİ", y="TOPLAM", data=box_data, ax=ax2, hue='KATEGORİ', palette='tab20')
plt.ylabel("Toplam Puan", fontsize='medium')
plt.xlabel("KATEGORİ", fontsize='medium')
ax2.tick_params(axis='both', which='major', labelsize=8)

fig2.savefig("figures/boxplot_category.png", bbox_inches="tight")
st.pyplot(fig2)
st.divider()

#################################################################################
# Klüplere Göre Toplam Puan Box-and-Whisker (Kutu) Grafiği
st.markdown("**Klüplere Göre Toplam Puan Puan Dağılım Grafiği**")
# Sadece yeterli sayıda sporcusu olan klüpler gösterilsin (ör: en az 5 sporcu)
club_counts = filtered_df[filtered_df["TOPLAM"] > 0]["KULÜB"].value_counts()
clubs_to_show = club_counts[club_counts >= 5].index  # En az 5 sporcusu olan klüpler

# Kulüp adlarını kısalt
def shorten_club_name(name):
    # "Spor Kulübü" ifadesini "SK" ile değiştir
    name = name.replace("SPOR KULÜBÜ", "SK")
    return name

club_box_data = filtered_df[
    (filtered_df["KULÜB"].isin(clubs_to_show)) & 
    (filtered_df["TOPLAM"] > 0)
].copy()
club_box_data["KULÜB"] = club_box_data["KULÜB"].apply(shorten_club_name)

if not club_box_data.empty:
    fig_club, ax_club = plt.subplots(figsize=(16, 8))
    sns.boxplot(x="KULÜB", y="TOPLAM", data=club_box_data, ax=ax_club, hue='KULÜB', palette='tab20')
    ax_club.set_ylabel("Toplam Puan")
    ax_club.set_xlabel("Kulüp")
    # Get current ticks and labels
    ticks = ax_club.get_xticks()
    labels = [label.get_text() for label in ax_club.get_xticklabels()]
    # Set ticks and labels explicitly
    ax_club.set_xticks(ticks)
    ax_club.set_xticklabels(labels, rotation='vertical', ha="right")

    fig_club.savefig("figures/boxplot_club.png", bbox_inches="tight")
    st.pyplot(fig_club)
    st.markdown("Yalnızca en az 5 sporcusu olan kulüpler gösterilmiştir.")
    st.markdown("*Not: Kulüp adları kısaltılmış olarak gösterilmektedir.*")
else:
    st.info("Yeterli sayıda sporcusu olan kulüp bulunamadı.")
st.divider()

#################################################################################
# 4. Her Kategori için Toplam Puan Histogramı (0 puan hariç)
st.subheader("**Her Kategori için Toplam Puan Histogramı (Katılmayanlar Hariç)**")
for kategori in filtered_df["KATEGORİ"].unique():
    st.markdown(f"### **{kategori}** kategorisi için toplam puan dağılımı:")
    fig, ax = plt.subplots(figsize=(16, 8))
    # Sadece 0'dan büyük puanlar
    data = filtered_df[(filtered_df["KATEGORİ"] == kategori) & (filtered_df["TOPLAM"] > 0)]["TOPLAM"].dropna()
    n, bins, patches = ax.hist(data, bins=21, color='skyblue', edgecolor='white')
    
    total = len(data)
    for count, patch in zip(n, patches):
        percentage = f'{(count/total)*100:.1f}%'
        plt.text(patch.get_x() + patch.get_width()/2, count, 
                s=int(count), #[int(count), percentage], 
                mouseover=True,
                ha='center', va='bottom', rotation='vertical',
                fontsize='medium',
                )
    
    plt.xticks(np.arange(0, 110, step=5), rotation='vertical')
    plt.yticks(np.arange(0, 10, step=10))
    ax.set_title(f"{kategori} Kategorisi Puan Dağılımı")
    ax.set_xlabel("Toplam Puan")
    ax.set_ylabel("Sporcu Sayısı")

    fig.savefig(f"figures/histogram_{kategori}.png", bbox_inches="tight")
    st.pyplot(fig)
    st.markdown(f"{kategori} kategorisinde (0 puan hariç) sporcuların toplam puanlarının dağılımı yukarıda gösterilmiştir.")

st.divider()
#################################################################################
# Açıklamalar
st.markdown("""
### Açıklamalar

- **Şehre Göre Ortalama Toplam Puan:** Hangi illerin ortalama olarak daha yüksek puan aldığını gösterir.
- **Kategoriye Göre Puan Dağılımı:** Kategoriler arasındaki puanların dağılımını ve ortalamasını karşılaştırır.
- **Şehre Göre Katılım Oranı:** Her ilden katılan sporcuların oranını görselleştirir.

Veriyi keşfetmek için kenar çubuğundaki filtreleri kullanabilirsiniz!
""")