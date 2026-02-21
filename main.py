import os
import requests
import json

# GitHub Secrets
TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_response(user_msg):
    """গুগলের সবথেকে স্টেবল এপিআই ব্যবহার করে উত্তর আনা"""
    if not GEMINI_API_KEY:
        return "❌ Error: GEMINI_API_KEY পাওয়া যায়নি।"

    # এই মডেলটি বর্তমানে সবথেকে বেশি সাপোর্ট করে
    model_id = "gemini-1.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={GEMINI_API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    prompt = f"You are a helpful assistant for Mintu Shop. Sell Watch (500 TK), Headphone (300 TK). Customer asked: {user_msg}. Answer in Bengali."
    
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        res_json = response.json()
        
        # যদি সাকসেস হয়
        if 'candidates' in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        # যদি এরর হয়, তবে সেটি বিস্তারিত দেখাবে
        elif 'error' in res_json:
            return f"❌ AI Error: {res_json['error']['message']}"
        else:
            return "🤖 AI এই মুহূর্তে কথা বলতে পারছে না।"
            
    except Exception as e:
        return f"⚠️ System Error: {str(e)}"

def handle_updates():
    """টেলিগ্রাম থেকে মেসেজ নিয়ে উত্তর দেওয়া"""
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    try:
        r = requests.get(url).json()
        if r.get("ok") and r.get("result"):
            last_id = 0
            for update in r["result"]:
                last_id = update["update_id"]
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"]["text"]
                    
                    print(f"মেসেজ পেয়েছেন: {text}")
                    reply = get_ai_response(text)
                    
                    # টেলিগ্রামে উত্তর পাঠানো
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                  json={"chat_id": chat_id, "text": reply})
            
            # মেসেজ ক্লিয়ার করা
            requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_id + 1}")
    except Exception as e:
        print(f"Telegram Error: {e}")

if __name__ == "__main__":
    if TOKEN:
        handle_updates()
