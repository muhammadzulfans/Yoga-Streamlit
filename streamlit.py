from wordcloud import WordCloud

import streamlit as st
import re
from collections import Counter
from pymongo import MongoClient
import matplotlib.pyplot as plt


#Koneksi MongoDB
uri = "mongodb+srv://<db_username>:<db_password>@capestone.o68xbne.mongodb.net/?retryWrites=true&w=majority&appName=capestone"
client = MongoClient(uri)
db = client['zenPoseDatabase']
berita = db['yogaNewsMultiSource']



# Menghapus kata sambung yang tidak penting
with open("sambungkata.txt", "r", encoding="utf-8") as f:
    stopwords = set(line.strip() for line in f.readlines())

st.title("Yoga Detection")
st.subheader("cok")
st.write("dancok")


with st.spinner("Processing..."):
    all_tokens = []

    for data in berita.find():
        isi = data.get('judul', '')
        isi = isi.lower()
        isi = re.sub('[^a-zA-Z]', '', isi)
        tokens = isi.split()

        #Stopword removal tanpa steaming
        tokens = [word for word in tokens if word not in stopwords]
        all_tokens.extend(tokens)

    counter = Counter(all_tokens)

    if counter:
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(counter)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    else:
        st.warning("Data berita kosong atau tidak dapat diproses.")