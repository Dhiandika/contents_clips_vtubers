import csv
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Konfigurasi Selenium untuk Edge
edge_options = Options()
edge_options.add_argument("--headless")  # Jalankan tanpa membuka browser (opsional)
edge_service = Service("C:/WebDriver/msedgedriver.exe")  # Ganti dengan lokasi msedgedriver Anda
driver = webdriver.Edge(service=edge_service, options=edge_options)

# URL website
url = "https://holoclips.net/#/"
driver.get(url)

# Debugging: Cek apakah halaman dimuat
print("Mengakses halaman:", url)

# Tunggu hingga elemen dengan id="container" muncul
try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "container"))
    )
    print("Kontainer utama ditemukan.")
except Exception as e:
    print("Error: Kontainer utama tidak selesai dimuat.")
    driver.quit()
    exit()

# Data untuk CSV
data_list = []

# Fungsi untuk ekstrak data dari kontainer
def extract_data():
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # Cari semua elemen card berdasarkan kelas "card"
    cards = soup.find_all("div", class_="card")
    print(f"Jumlah elemen card ditemukan: {len(cards)}")

    if len(cards) == 0:
        print("Tidak ada elemen card yang ditemukan.")
        return

    # Loop setiap card dan ambil data
    for index, card in enumerate(cards, start=1):
        try:
            # Judul Video
            title_element = card.find("div", class_="video-title").find("p")
            title = title_element.get_text(strip=True) if title_element else "No Title"

            # Durasi
            duration_element = card.find("span", class_="duration")
            duration = duration_element.get_text(strip=True) if duration_element else "No Duration"

            # Author
            author_element = card.find("div", class_="video-info").find("p")
            author = author_element.get_text(strip=True) if author_element else "No Author"

            # Link Video
            link_element = card.find("a", href=True)
            video_link = link_element["href"] if link_element else "No Link"

            # Thumbnail
            thumbnail_element = card.find("img", src=True)
            thumbnail = thumbnail_element["src"] if thumbnail_element else "No Thumbnail"

            # Simpan ke list
            data_list.append({
                "title": title,
                "duration": duration,
                "author": author,
                "video_link": video_link,
                "thumbnail": thumbnail
            })

            # Debugging: Cetak data untuk setiap card
            print(f"Card {index}:")
            print(f"  Title: {title}")
            print(f"  Duration: {duration}")
            print(f"  Author: {author}")
            print(f"  Video Link: {video_link}")
            print(f"  Thumbnail: {thumbnail}")

        except Exception as e:
            print(f"Error saat membaca card {index}: {e}")
            continue

# Ekstrak data dari halaman saat ini
extract_data()

# Tutup driver
driver.quit()

# Simpan data ke CSV
csv_filename = "holoclips_data_current_page.csv"
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["title", "duration", "author", "video_link", "thumbnail"])
    writer.writeheader()
    writer.writerows(data_list)

# Debugging: Tampilkan jumlah data yang diekstrak
print(f"Total data yang diekstrak: {len(data_list)}")
print(f"Data telah disimpan ke {csv_filename}")
