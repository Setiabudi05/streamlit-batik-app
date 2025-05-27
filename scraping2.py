import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import datetime

# Koneksi ke MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['BatikKara']
collection = db['berita_edukasibudaya']

# Scraping dari Detik
def scrape_detik():
    url = "https://www.detik.com/tag/batik/"
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[Detik] Gagal mengambil data: {e}")
        return

    soup = BeautifulSoup(r.content, 'html.parser')
    articles = []

    for item in soup.select('article'):
        title_tag = item.find('h2') or item.find('h3')
        if not title_tag:
            continue

        link_tag = title_tag.find('a')
        if not link_tag:
            continue

        title = title_tag.get_text(strip=True)
        link = link_tag['href']

        if not collection.find_one({'link': link}):
            articles.append({
                'sumber': 'detik',
                'judul': title,
                'link': link,
                'tanggal_scrape': datetime.datetime.now()
            })

    if articles:
        collection.insert_many(articles)
        print(f"{len(articles)} artikel dari Detik berhasil disimpan.")
    else:
        print("[Detik] Tidak ada artikel baru.")

# Scraping dari Media Indonesia
def scrape_mediaindonesia():
    url = "https://mediaindonesia.com/tag/batik"
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[MediaIndonesia] Gagal mengambil data: {e}")
        return

    soup = BeautifulSoup(r.content, 'html.parser')
    articles = []

    for item in soup.select('.card-horizontal'):
        title_tag = item.find('h2') or item.find('h3')
        if not title_tag:
            continue

        link_tag = title_tag.find('a')
        if not link_tag:
            continue

        title = title_tag.get_text(strip=True)
        link = link_tag['href']
        if link and not link.startswith("http"):
            link = "https://mediaindonesia.com" + link

        if not collection.find_one({'link': link}):
            articles.append({
                'sumber': 'mediaindonesia',
                'judul': title,
                'link': link,
                'tanggal_scrape': datetime.datetime.now()
            })

    if articles:
        collection.insert_many(articles)
        print(f"{len(articles)} artikel dari Media Indonesia berhasil disimpan.")
    else:
        print("[MediaIndonesia] Tidak ada artikel baru.")

# Jalankan scraping
scrape_detik()
scrape_mediaindonesia()
