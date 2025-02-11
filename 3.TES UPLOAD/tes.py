import requests
import os
from dotenv import load_dotenv

# Memuat variabel dari file .env
load_dotenv()

CLIENT_KEY = os.getenv("CLIENT_KEY")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

def upload_video(video_path, title, description):
    url = "https://open-api.tiktok.com/video/upload/"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    
    files = {
        "video": open(video_path, "rb")
    }
    
    data = {
        "title": title,
        "description": description
    }
    
    response = requests.post(url, headers=headers, files=files, data=data)
    
    if response.status_code == 200:
        print("Video berhasil diunggah:", response.json())
    else:
        print("Gagal mengunggah video:", response.text)

# Contoh penggunaan dengan file video dan data dari CSV
upload_video("path/ke/video.mp4", "Judul Video", "Deskripsi video dengan hashtag")
