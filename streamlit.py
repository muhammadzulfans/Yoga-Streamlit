from wordcloud import WordCloud
import streamlit as st
import re
from collections import Counter
from pymongo import MongoClient
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Setup gaya visual
sns.set(style="whitegrid")
plt.rcParams.update({
    "axes.titlesize": 16,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "axes.titleweight": 'bold'
})

# Koneksi MongoDB
uri = "mongodb+srv://zenpose:capstone12345@capestone.o68xbne.mongodb.net/?retryWrites=true&w=majority&appName=capestone"
client = MongoClient(uri)
db = client['zenPoseDatabase']
berita = db['yogaNewsMultiSource']

# Load stopwords
with open("sambungkata.txt", "r", encoding="utf-8") as f:
    stopwords = set(line.strip() for line in f.readlines())

# Streamlit UI
st.title("🧘‍♀️ Yoga News Dashboard")
st.markdown("Visualisasi data berita seputar yoga dari berbagai sumber media.")
st.markdown("---")

with st.spinner("Processing..."):
    all_tokens = []
    sumber_counter = Counter()
    total_artikel = 0

    for data in berita.find():
        total_artikel += 1

        # Hitung jumlah artikel per sumber
        sumber = data.get('sumber', 'Tidak diketahui')
        sumber_counter[sumber] += 1

        # Proses teks judul
        isi = data.get('judul', '')
        isi = isi.lower()
        isi = re.sub(r'[^a-zA-Z\s]', '', isi)
        tokens = isi.split()
        tokens = [word for word in tokens if word not in stopwords]
        all_tokens.extend(tokens)

    # Tampilkan total artikel
    st.metric("📰 Total Artikel", total_artikel)

    # Tampilkan jumlah artikel per sumber
    if sumber_counter:
        st.subheader("📊 Jumlah Artikel per Sumber")
        sumber_df = pd.DataFrame(sumber_counter.items(), columns=['Sumber', 'Jumlah Artikel'])

        # Sort dan plot
        sumber_df = sumber_df.sort_values(by='Jumlah Artikel', ascending=False)
        fig_sumber, ax_sumber = plt.subplots(figsize=(10, 6))
        palette = sns.color_palette("pastel")
        sns.barplot(x='Jumlah Artikel', y='Sumber', data=sumber_df, palette=palette, ax=ax_sumber)
        ax_sumber.set_title("Distribusi Artikel per Sumber Media")
        ax_sumber.set_xlabel("Jumlah Artikel")
        ax_sumber.set_ylabel("Sumber Media")
        plt.tight_layout()
        st.pyplot(fig_sumber)
    else:
        st.warning("Tidak ditemukan informasi sumber dalam artikel.")

    # WordCloud
    counter = Counter(all_tokens)
    if counter:
        st.subheader("☁️ Word Cloud Judul Artikel")
        wordcloud = WordCloud(width=1000, height=500, background_color='white', colormap='viridis').generate_from_frequencies(counter)
        fig_wc, ax_wc = plt.subplots(figsize=(12, 6))
        ax_wc.imshow(wordcloud, interpolation='bilinear')
        ax_wc.axis('off')
        plt.tight_layout()
        st.pyplot(fig_wc)
    else:
        st.warning("Tidak ada kata yang bisa diproses dari judul.")
