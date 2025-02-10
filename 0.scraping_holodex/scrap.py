import requests
import csv
import os
from dotenv import load_dotenv

# Load API key dari .env file
load_dotenv()
API_KEY = os.getenv("X_APIKEY")

# Konfigurasi limit awal
USER_LIMIT = 50  # Bisa diubah sesuai keinginan (maks 50)
INCREMENT_STEP = 50  # Bertambah setiap iterasi
MAX_TOTAL = 270000  # Maksimal total data yang ingin diambil (bisa diatur)

def fetch_holodex_data(limit, offset):
    """Mengambil data dari Holodex API berdasarkan limit dan offset."""
    url = "https://holodex.net/api/v2/videos"
    params = {
        "status": "past",
        "type": "clip",
        "lang": "id,en",
        "paginated": "true",
        "org": "All Vtubers",
        "limit": limit,
        "offset": offset
    }
    headers = {
        "Content-Type": "application/json",
        "X-APIKEY": API_KEY
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get("items", []), data.get("total", 0)
    else:
        print(f"Failed to fetch data (Status: {response.status_code})")
        return [], 0

def save_to_csv(data, filename="holodex_data.csv"):
    """Menyimpan data ke dalam file CSV."""
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Tulis header jika file baru dibuat
        if not file_exists:
            writer.writerow(["id", "title", "duration", "lang", "author_name", "published_at"])
        
        for item in data:
            writer.writerow([
                item.get("id", ""),
                item.get("title", ""),
                item.get("duration", ""),
                item.get("lang", ""),
                item.get("channel", {}).get("name", ""),
                item.get("published_at", "")
            ])
    
    print(f"{len(data)} items saved to {filename}")

if __name__ == "__main__":
    offset = 0
    current_limit = USER_LIMIT
    total_fetched = 0

    while total_fetched < MAX_TOTAL:
        print(f"Fetching {current_limit} items (Offset: {offset})...")
        video_data, total_available = fetch_holodex_data(current_limit, offset)

        if not video_data:
            print("No more data available or an error occurred.")
            break

        save_to_csv(video_data)
        total_fetched += len(video_data)
        offset += len(video_data)

        # Jika data yang diambil kurang dari limit, hentikan loop (tidak ada data tersisa)
        if len(video_data) < current_limit:
            print("No more data left to fetch.")
            break

        # Tambah limit dengan kelipatan jika masih ada data
        if current_limit + INCREMENT_STEP <= 50:  # Tetap dalam batas limit API (<=50)
            current_limit += INCREMENT_STEP

    print("Finished fetching all data.")
