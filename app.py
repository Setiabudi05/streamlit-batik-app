import streamlit as st
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import seaborn as sns
import re
from collections import Counter

# Konfigurasi Streamlit
st.set_page_config(page_title="Dashboard Batikkara", layout="wide")

# Koneksi MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['BatikKara']
collection = db['berita_edukasibudaya']

# Ambil data
data = list(collection.find())
df = pd.DataFrame(data)

# Judul Aplikasi
st.markdown("""
    <h1 style='text-align: center; color: #007acc;'>📊 Dashboard Berita Budaya</h1>
    <p style='text-align: center;'>Visualisasi hasil scraping dari berbagai sumber berita bertema budaya.</p>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🔍 Filter & Info")
    st.markdown(f"Total Artikel: *{len(df)}*")
    sumber_unik = df['source'].unique()
    sumber_filter = st.multiselect("Pilih sumber berita:", sumber_unik, default=sumber_unik)

# Filter
filtered_df = df[df['source'].isin(sumber_filter)]

# Visualisasi 1: Jumlah Artikel per Sumber Berita
st.subheader("📈 Jumlah Artikel per Sumber Berita")
fig1, ax1 = plt.subplots(figsize=(10, 5))
filtered_df['source'].value_counts().plot(kind='bar', ax=ax1, color='#28a745')
ax1.set_xlabel('Sumber Berita')
ax1.set_ylabel('Jumlah Artikel')
plt.xticks(rotation=45)
st.pyplot(fig1)

# Visualisasi 2: Word Cloud Judul Artikel dengan Stopword Removal
st.subheader("☁️ Word Cloud dari Judul Artikel")

# Stopwords bawaan dan tambahan Bahasa Indonesia
stopwords = set(STOPWORDS)
stopwords.update([
    'yang', 'dan', 'di', 'ke', 'dari', 'untuk', 'dengan', 'pada',
    'ini', 'itu', 'dalam', 'akan', 'karena', 'sebagai', 'adalah',
    'berita', 'budaya', 'tentang', 'oleh', 'atau', 'jadi'
])

# Gabungkan teks dan bersihkan
text = ' '.join(filtered_df['judul'].fillna('').tolist()).lower()
text = re.sub(r'\d+', '', text)                 # hapus angka
text = re.sub(r'[^\w\s]', '', text)             # hapus tanda baca
filtered_words = ' '.join([word for word in text.split() if word not in stopwords])

# Buat dan tampilkan Word Cloud
wordcloud = WordCloud(width=1000, height=400, background_color='white').generate(filtered_words)
fig_wc, ax_wc = plt.subplots(figsize=(12, 4))
ax_wc.imshow(wordcloud, interpolation='bilinear')
ax_wc.axis('off')
st.pyplot(fig_wc)


# Visualisasi 3: Jumlah Artikel per Tanggal
if 'tanggal' in filtered_df.columns:
    st.subheader("📅 Jumlah Artikel per Tanggal Publikasi")
    filtered_df['tanggal'] = pd.to_datetime(filtered_df['tanggal'], errors='coerce')
    artikel_per_tanggal = filtered_df.groupby(filtered_df['tanggal'].dt.date).size()
    fig3, ax3 = plt.subplots(figsize=(12, 4))
    artikel_per_tanggal.plot(kind='line', marker='o', color='#ff9933', ax=ax3)
    ax3.set_xlabel("Tanggal")
    ax3.set_ylabel("Jumlah Artikel")
    plt.xticks(rotation=45)
    st.pyplot(fig3)
    
# Tokenisasi dan Hitung Kata Terpopuler (tanpa angka & stopword)
judul_text = ' '.join(filtered_df['judul'].fillna('').tolist()).lower()
judul_text = re.sub(r'[^\w\s]', '', judul_text)  # hapus tanda baca

# Hapus stopword dan angka
kata_list = [
    word for word in judul_text.split()
    if word not in stopwords and word.isalpha()
]

# Ambil 10 kata terpopuler
top_kata = Counter(kata_list).most_common(10)
kata_df = pd.DataFrame(top_kata, columns=['Kata', 'Jumlah'])

# Visualisasi
fig6, ax6 = plt.subplots(figsize=(10, 5))
sns.barplot(x='Jumlah', y='Kata', data=kata_df, ax=ax6, palette='viridis')
ax6.set_title("10 Kata Terpopuler di Judul Artikel")
st.pyplot(fig6)


# Visualisasi Card: Daftar Berita Budaya
st.subheader("📰 Daftar Berita Budaya")
col1, col2, col3 = st.columns(3)
cols = [col1, col2, col3]
for idx, row in filtered_df.iterrows():
    with cols[idx % 3]:
        st.markdown(f"""
        <div style='border: 1px solid #ccc; border-radius: 12px; padding: 15px; margin-bottom: 15px; background-color: #f9f9f9;'>
            <h4 style='margin-bottom: 10px;'>{row['judul']}</h4>
            <p style='font-size: 14px; color: #555;'>{row.get('description', '-')[:100]}...</p>
            <a href='{row['link']}' target='_blank'>🔗 Baca selengkapnya</a>
        </div>
        """, unsafe_allow_html=True)
