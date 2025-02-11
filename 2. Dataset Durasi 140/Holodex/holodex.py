import os
import csv
import yt_dlp
from datetime import datetime, timedelta

# Konfigurasi
INPUT_CSV = "holodex_data_id_filtered.csv"
OUTPUT_DIR = "downloaded_videos"
VIDEOS_PER_DAY = 10
DEBUG_MODE = True
CHECKPOINT_FILE = "checkpoint.txt"
QUALITY_LOG_FILE = "quality_log.txt"
DAYS_TO_DOWNLOAD = 7
PREFERRED_QUALITY = "1080p"

QUALITY_OPTIONS = ["1080p", "720p", "480p", "360p", "best"]

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
            videos.append({
                "id": row["id"],
                "title": row["title"],
                "author_name": f"Youtube: {row['author_name']}"  # Tambahkan "Youtube: "
            })
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

def save_quality_log(video_id, quality):
    """Menyimpan log kualitas video yang berhasil diunduh."""
    with open(QUALITY_LOG_FILE, "a") as f:
        f.write(f"{video_id}: {quality}\n")

def get_best_quality():
    """Mengembalikan format yt-dlp untuk kualitas yang tersedia."""
    quality_str = ",".join([f"bestvideo[height={q[:-1]}]+bestaudio/best" for q in QUALITY_OPTIONS])
    return quality_str

def download_video(video_id, author, output_path, video_number):
    """Mengunduh video dari YouTube menggunakan yt-dlp."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    filename = f"{video_number} {author} - {video_id}.mp4".replace("/", "_").replace("\\", "_")
    filepath = os.path.join(output_path, filename)

    if os.path.exists(filepath):
        print(f"[SKIP] Video {filename} sudah ada.")
        return filepath

    log_debug(f"Mengunduh: {url} dengan kualitas {PREFERRED_QUALITY}")

    ydl_opts = {
        "format": get_best_quality(),
        "outtmpl": filepath,
        "noplaylist": True,
        "quiet": not DEBUG_MODE,
        "continuedl": True,  # Resume jika gagal
        "merge_output_format": "mp4",
        "progress_hooks": [lambda d: log_debug(f"Status: {d['status']}")] if DEBUG_MODE else None,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.download([url])
            if result == 0:
                log_debug(f"Berhasil mengunduh {filename}")
                save_checkpoint(video_id)
                save_quality_log(video_id, PREFERRED_QUALITY)
                return filepath
            else:
                print(f"[ERROR] Gagal mengunduh {video_id}")
                return None

    except yt_dlp.DownloadError as e:
        error_message = str(e).lower()
        if "private" in error_message or "unavailable" in error_message or "403" in error_message:
            print(f"[SKIP] Video {video_id} tidak tersedia atau private.")
        else:
            print(f"[ERROR] Gagal mengunduh {video_id}: {e}")
        return None

def save_csv(data, output_file):
    """Menyimpan data ke dalam file CSV dengan format yang diinginkan dan menjaga urutan."""
    if not data:
        return
    keys = ["id", "title", "author_name"]
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

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

        processed_videos = []  # List untuk menyimpan video yang telah berhasil diunduh
        video_number = 1  # Mulai penomoran dari 1 untuk setiap folder baru

        for video in video_batches[i]:
            video_id = video['id']
            author = video['author_name'].replace("Youtube: ", "")  # Hilangkan 'Youtube: ' dari nama file

            if video_id in completed_videos:
                print(f"[SKIP] Video {video_id} sudah diunduh sebelumnya.")
                continue

            filepath = download_video(video_id, author, folder_path, video_number)
            if filepath:
                processed_videos.append(video)  # Tambahkan ke daftar dalam urutan unduhan
                video_number += 1  # Naikkan nomor untuk video berikutnya

        if processed_videos:
            csv_output = os.path.join(folder_path, "videos.csv")
            save_csv(processed_videos, csv_output)
            print(f"[SAVED] CSV untuk {date_folder} di {csv_output}")

def main():
    videos = read_csv(INPUT_CSV)
    distribute_videos(videos)
    print("[DONE] Semua video telah diproses.")

if __name__ == "__main__":
    main()
