from flask import Flask
from pyngrok import ngrok

app = Flask(__name__)

# Buka akses publik
public_url = ngrok.connect(5000).public_url
print(f"Ngrok URL: {public_url}")

@app.route("/")
def home():
    return "Server is running"

if __name__ == "__main__":
    app.run(port=5000)
