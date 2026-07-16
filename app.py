import os
import urllib.request
import urllib.parse
import json
from flask import Flask, request

app = Flask(__name__)
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if update and "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        
        if text == "/start":
            reply = "🎫 Baga nagaan dhuftan! Bot-iin Eqqub keesanii sirriitti hojjechaa jira."
            # Bakka kanatti liinkiin Telegram API bifa kanaan sirriitti ijaarameera
            url = f"https://telegram.org{TOKEN}/sendMessage"
            
            payload = {"chat_id": chat_id, "text": reply}
            data = urllib.parse.urlencode(payload).encode("utf-8")
            
            try:
                req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
                urllib.request.urlopen(req)
            except Exception as e:
                print("Error sending message:", e)
                
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
