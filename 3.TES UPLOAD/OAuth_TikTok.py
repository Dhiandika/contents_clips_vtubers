import os
import requests
from flask import Flask, request, redirect
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

CLIENT_KEY = os.getenv("CLIENT_KEY")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

app = Flask(__name__)

# Step 1: Redirect pengguna ke TikTok untuk login
@app.route("/")
def login():
    auth_url = (
        f"https://www.tiktok.com/auth/authorize/"
        f"?client_key={CLIENT_KEY}"
        f"&scope=user.info.basic,video.upload"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&state=random_state"
    )
    return redirect(auth_url)

# Step 2: TikTok mengembalikan Authorization Code
@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Authorization failed", 400
    
    # Step 3: Tukar Authorization Code dengan Access Token
    token_url = "https://open-api.tiktok.com/oauth/access_token/"
    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        return f"Access Token: {access_token} (Simpan ini di .env)"
    else:
        return f"Failed to get access token: {response.text}"

if __name__ == "__main__":
    app.run(port=5000, debug=True)
