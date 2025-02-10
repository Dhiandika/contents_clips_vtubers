import os
import csv
import subprocess
from datetime import datetime, timedelta

# Konfigurasi
INPUT_CSV = "holodex_data_id_filtered.csv"
OUTPUT_DIR = "downloaded_videos"
VIDEOS_PER_DAY = 10  # Maksimal video per hari
DEBUG_MODE = True  # Aktifkan debugging
CHECKPOINT_FILE = "checkpoint.txt"  # File untuk menyimpan progress
DAYS_TO_DOWNLOAD = 7  # Ubah sesuai kebutuhan, misalnya 30 untuk sebulan

def log_debug(message):
    """Mencetak pesan debug jika mode debugging aktif."""
    if DEBUG_MODE:
        print(f"[DEBUG] {message}")

def read_csv(file_path):
    """Membaca data dari CSV dan mengembalikan daftar video yang belum diunduh."""
    videos = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            videos.append(row)
    return videos

def load_checkpoint():
    """Memuat daftar video yang sudah diunduh untuk melanjutkan unduhan."""
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            completed_videos = set(f.read().splitlines())
            return completed_videos
    return set()

def save_checkpoint(video_id):
    """Menyimpan ID video yang sudah berhasil diunduh."""
    with open(CHECKPOINT_FILE, "a") as f:
        f.write(video_id + "\n")

def download_video(video_id, author, output_path):
    """Mengunduh video dari YouTube menggunakan yt-dlp."""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        filename = f"{author} - {video_id}.mp4".replace("/", "_").replace("\\", "_")  # Hindari karakter ilegal
        filepath = os.path.join(output_path, filename)

        if os.path.exists(filepath):
            print(f"[SKIP] Video {filename} sudah ada.")
            return filepath

        log_debug(f"Mengunduh: {url}")
        command = [
            "yt-dlp", "-f", "best", "-o", filepath, url
        ]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            log_debug(f"Berhasil mengunduh {filename}")
            save_checkpoint(video_id)
            return filepath
        else:
            error_message = result.stderr.lower()
            if "private" in error_message or "unavailable" in error_message:
                print(f"[SKIP] Video {video_id} tidak tersedia atau private.")
            else:
                print(f"[ERROR] Gagal mengunduh {video_id}: {result.stderr}")
            return None

    except Exception as e:
        print(f"[ERROR] Gagal mengunduh {video_id}: {e}")
        return None

def save_csv(data, output_file):
    """Menyimpan data ke dalam file CSV dengan format yang diinginkan."""
    if not data:
        return
    keys = ["id", "title", "author_name"]
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for row in data:
            row["author_name"] = f"Youtube: {row['author_name']}"  # Tambahkan "Youtube:" di depan author_name
            writer.writerow(row)


def save_csv(data, output_file):
    """Menyimpan data ke dalam file CSV dengan format yang diinginkan."""
    if not data:
        return
    keys = ["id", "title", "author_name"]
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

def format_date_folder(date):
    """Mengembalikan nama folder dalam format 'DD-MMMM'."""
    return date.strftime('%d-%B')

def distribute_videos(videos):
    """Membagi video ke dalam folder berdasarkan hari dan melanjutkan dari checkpoint."""
    today = datetime.today()
    completed_videos = load_checkpoint()

    video_batches = [videos[i:i + VIDEOS_PER_DAY] for i in range(0, len(videos), VIDEOS_PER_DAY)]

    for i in range(min(len(video_batches), DAYS_TO_DOWNLOAD)):
        date_folder = format_date_folder(today + timedelta(days=i))
        folder_path = os.path.join(OUTPUT_DIR, date_folder)
        os.makedirs(folder_path, exist_ok=True)

        processed_videos = []
        for video in video_batches[i]:
            video_id = video['id']
            author = video['author_name']

            if video_id in completed_videos:
                print(f"[SKIP] Video {video_id} sudah diunduh sebelumnya.")
                continue

            filepath = download_video(video_id, author, folder_path)
            if filepath:
                processed_videos.append({
                    "id": video["id"],
                    "title": video["title"],
                    "author_name": video["author_name"]
                })

        if processed_videos:
            csv_output = os.path.join(folder_path, "videos.csv") # TODO: ubah ini sesuai kebutuhan
            save_csv(processed_videos, csv_output)
            print(f"[SAVED] CSV untuk {date_folder} di {csv_output}")

def main():
    videos = read_csv(INPUT_CSV)
    distribute_videos(videos)
    print("[DONE] Semua video telah diproses.")

if __name__ == "__main__":
    main()
