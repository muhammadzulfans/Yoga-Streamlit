import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient
from wordcloud import WordCloud, STOPWORDS
import re
from collections import Counter
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()
uri = "mongodb+srv://zenpose:capstone12345@capestone.o68xbne.mongodb.net/?retryWrites=true&w=majority&appName=capestone"
client = MongoClient(uri)
db = client['zenPoseDatabase']
collection = db['yogaNewsMultiSource']
st.set_page_config(layout="wide")

sns.set(style="whitegrid")
plt.rcParams.update({
    "axes.titlesize": 16,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "axes.titleweight": 'bold'
})

client = MongoClient(uri)
db = client['zenPoseDatabase']
collection = db['yogaNewsMultiSource']

@st.cache_data
def load_data():
    data = list(collection.find())
    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset='url')
    df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
    return df

def clean_text(text, stopwords):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    tokens = text.split()
    return [t for t in tokens if t not in stopwords]

def load_stopwords():
    try:
        with open("sambungkata.txt", "r", encoding="utf-8") as f:
            custom = set(line.strip() for line in f.readlines())
    except Exception:
        custom = set()
    return custom.union(STOPWORDS)

st.markdown(
    """
    <style>
    .reportview-container .main .block-container{
        max-width: 1200px;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🧘‍♀️ Yoga News Dashboard")

df = load_data()

if df.empty:
    st.warning("Tidak ada data ditemukan dalam koleksi MongoDB.")
    st.stop()

st.metric("📰 Total Artikel", len(df))
st.markdown("<br><br>", unsafe_allow_html=True)
st.subheader("🗂️ Daftar Artikel")
df_display = df[['judul', 'url']].dropna().reset_index(drop=True)
df_display.columns = ['Judul Artikel', 'Link']

fullsize = st.checkbox("View Full Size Table", value=False)
table_height = 600 if fullsize else 300
st.dataframe(df_display, height=table_height)

st.markdown("<br><br>", unsafe_allow_html=True)

st.subheader("☁️ Word Cloud dari Judul Artikel")

all_titles = " ".join(df['judul'].dropna())
tokens = clean_text(all_titles, load_stopwords())
token_counts = Counter(tokens)

if token_counts:
    wordcloud = WordCloud(
        width=1000,
        height=500,
        background_color='white',
        colormap='viridis',
        max_words=50
    ).generate_from_frequencies(token_counts)

    fig_wc, ax_wc = plt.subplots(figsize=(12, 6))
    ax_wc.imshow(wordcloud, interpolation='bilinear')
    ax_wc.axis('off')
    st.pyplot(fig_wc)
else:
    st.info("Tidak ada cukup kata untuk membuat Word Cloud.")

st.markdown("<br><br>", unsafe_allow_html=True)
st.subheader("📈 Tren Kata Terbanyak (Top 20)")

most_common = token_counts.most_common(20)
wc_df = pd.DataFrame(most_common, columns=["Kata", "Frekuensi"])
wc_df = wc_df.sort_values(by="Frekuensi", ascending=True)

fig_wc2, ax_wc2 = plt.subplots(figsize=(12, 6), facecolor='none')
colors_wc = plt.cm.Blues(np.linspace(0.4, 1, len(wc_df)))

bars_wc = ax_wc2.barh(wc_df['Kata'], wc_df['Frekuensi'], color=colors_wc)

ax_wc2.xaxis.grid(True, linestyle='--', linewidth=0.5, alpha=0.3)
ax_wc2.yaxis.grid(False)
for spine in ax_wc2.spines.values():
    spine.set_visible(False)

ax_wc2.set_facecolor('none')
ax_wc2.set_xlabel("Frekuensi", color='white')
ax_wc2.set_ylabel("Kata", color='white')
ax_wc2.tick_params(axis='x', colors='white')
ax_wc2.tick_params(axis='y', colors='white')

for bar in bars_wc:
    width = bar.get_width()
    ax_wc2.text(width, bar.get_y() + bar.get_height()/2, f'{int(width)}',
                ha='left', va='center', color='white', fontsize=9)

plt.tight_layout()
st.pyplot(fig_wc2)

st.markdown("<br><br>", unsafe_allow_html=True)

st.subheader("📌 Jumlah Artikel per Sumber")
sumber_counts = df['sumber'].value_counts().reset_index()
sumber_counts.columns = ['Sumber', 'Jumlah Artikel']
fig, ax = plt.subplots(figsize=(14, 7), facecolor='none')
colors_sumber = plt.cm.Blues(np.linspace(0.4, 1, len(sumber_counts)))
bars_sumber = ax.bar(sumber_counts['Sumber'], sumber_counts['Jumlah Artikel'], color=colors_sumber, width=0.6)

ax.yaxis.grid(True, linestyle='--', linewidth=0.5, alpha=0.3)
ax.xaxis.grid(False)
for spine in ax.spines.values():
    spine.set_visible(False)

ax.set_xlabel("Sumber Media", color='white')
ax.set_ylabel("Jumlah Artikel", color='white')
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', color='white')
ax.set_yticklabels(ax.get_yticks(), color='white')
ax.set_facecolor('none')

for bar in bars_sumber:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, height, f'{int(height)}',
            ha='center', va='bottom', color='white', fontsize=9)

plt.tight_layout()
st.pyplot(fig)
