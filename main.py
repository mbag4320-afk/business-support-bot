import os
import requests

TOKEN = os.getenv("BOT_TOKEN")
OWNER_CHAT_ID = os.getenv("CHAT_ID")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

def get_ai_response(user_msg):
    try:
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}
        system_info = "You are a helpful Bengali assistant for Mintu Shop. Sell gadgets like Watch-500TK, Headphone-300TK."
        data = {
            "model": "open-mistral-7b",
            "messages": [
                {"role": "system", "content": system_info},
                {"role": "user", "content": user_msg}
            ]
        }
        r = requests.post(url, headers=headers, json=data, timeout=15)
        print("Mistral AI Response Status:", r.status_code) # লগ চেক করার জন্য
        return r.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print("Mistral API Error:", e)
        return "আমাদের কাস্টমার কেয়ারে কল করুন।"

def handle_updates():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    r = requests.get(url)
    updates = r.json()
    
    if updates.get("ok") and updates.get("result"):
        print(f"Found {len(updates['result'])} new messages.")
        for update in updates["result"]:
            chat_id = update["message"]["chat"]["id"]
            user_text = update["message"]["text"]
            
            print(f"Replying to user: {chat_id}")
            reply = get_ai_response(user_text)
            
            send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            res = requests.post(send_url, json={"chat_id": chat_id, "text": reply})
            print("Telegram send response:", res.json())
    else:
        print("No unread messages found in Telegram.")

if __name__ == "__main__":
    handle_updates()
