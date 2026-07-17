import os
import urllib.request
import urllib.parse
import json
from flask import Flask, request

app = Flask(__name__)

# Token sirriitti dubbisuuf
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '').strip()

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if update and "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        
        if text == "/start":
            reply = "🎫 Baga nagaan dhuftan! Bot-iin Eqqub keesanii sirriitti hojjechaa jira."
            
            # Dogoggora 'nonnumeric port' maqsuuf liinkii bifa kanaan fidhanna
            url = f"https://telegram.org{BOT_TOKEN}/sendMessage"
            
            payload = {
                "chat_id": str(chat_id),
                "text": reply
            }
            
            data = urllib.parse.urlencode(payload).encode("utf-8")
            
            try:
                # Headers eegumsa qabu dabalanii erguu
                req = urllib.request.Request(
                    url, 
                    data=data, 
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
                urllib.request.urlopen(req)
                print(f"Message sent successfully to {chat_id}")
            except Exception as e:
                print("Error sending message from bot:", e)
                
    return "OK", 200
    @app.route('/')
    def home():
        return "Bot is running successfully with 200 OK!", 200
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

