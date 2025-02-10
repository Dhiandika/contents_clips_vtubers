import csv
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Konfigurasi Selenium untuk Edge
edge_options = Options()
edge_options.add_argument("--headless")  # Jalankan tanpa membuka browser (opsional)
edge_service = Service("C:/WebDriver/msedgedriver.exe")  # Ganti dengan lokasi msedgedriver Anda
driver = webdriver.Edge(service=edge_service, options=edge_options)

# URL website
url = "https://holoclips.net/#/"
driver.get(url)

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

        except Exception as e:
            print(f"Error saat membaca card {index}: {e}")
            continue

# Fungsi untuk navigasi ke halaman berikutnya
def navigate_to_next_page():
    try:
        next_button = driver.find_element(By.XPATH, '//div[@class="pagination-div ng-tns-c88-2"]//a[contains(text(), ">")]')
        next_button.click()
        time.sleep(3)  # Cooldown untuk memastikan halaman berikutnya termuat
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "card"))
        )  # Tunggu hingga elemen card muncul di halaman baru
        return True
    except Exception as e:
        print("Tidak ada halaman berikutnya.")
        return False

# Ekstrak data dari beberapa halaman
max_pages = int(input("Ingin scraping berapa halaman? (Masukkan 0 untuk semua halaman): "))
current_page = 1

while max_pages == 0 or current_page <= max_pages:
    print(f"Scraping halaman {current_page}...")
    extract_data()

    if not navigate_to_next_page():
        break
    current_page += 1

# Tutup driver
driver.quit()

# Simpan data ke CSV
csv_filename = "holoclips_data.csv"
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["title", "duration", "author", "video_link", "thumbnail"])
    writer.writeheader()
    writer.writerows(data_list)

print(f"Total data yang diekstrak: {len(data_list)}")
print(f"Data telah disimpan ke {csv_filename}")
