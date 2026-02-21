import os
import requests

# GitHub Secrets থেকে তথ্য নেওয়া
TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("AIzaSyARc-IoUyygjHTjr5xytu5HeNCZk21Q9vg")

def get_ai_response(user_msg):
    """Google Gemini AI ব্যবহার করে উত্তর দেওয়া"""
    if not GEMINI_API_KEY:
        return "ধন্যবাদ, আমরা শীঘ্রই যোগাযোগ করব।"
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        prompt = f"You are a helpful Bengali assistant for Mintu Shop. Sell gadgets like Watch-500TK, Headphone-300TK. Customer asked: {user_msg}. Answer briefly in Bengali."
        
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        r = requests.post(url, headers=headers, json=data, timeout=15)
        return r.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"AI Error: {e}")
        return "আমাদের কাস্টমার কেয়ারে কল করুন।"

def handle_updates():
    """মেসেজ চেক করে উত্তর পাঠানো"""
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    try:
        updates = requests.get(url).json()
        if updates.get("ok") and updates.get("result"):
            for update in updates["result"]:
                chat_id = update["message"]["chat"]["id"]
                user_text = update["message"]["text"]
                
                # AI উত্তর তৈরি
                reply = get_ai_inspiration = get_ai_response(user_text)
                
                # উত্তর পাঠানো
                send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                requests.post(send_url, json={"chat_id": chat_id, "text": reply})
    except Exception as e:
        print(f"Telegram Error: {e}")

if __name__ == "__main__":
    handle_updates()
