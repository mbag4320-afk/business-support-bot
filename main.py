import os
import requests

# GitHub Secrets থেকে তথ্য নেওয়া
TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_response(user_msg):
    """Google Gemini AI ব্যবহার করে স্মার্ট উত্তর তৈরি করা"""
    if not GEMINI_API_KEY:
        return "❌ Error: GEMINI_API_KEY পাওয়া যাচ্ছে না।"

    try:
        # লিঙ্কটি v1beta থেকে বদলে v1 (Stable) করা হয়েছে
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        
        # আপনার বিজনেসের তথ্য
        prompt = f"You are a professional Bengali assistant for 'Mintu Shop'. We sell Watch (500 TK) and Headphones (300 TK). Customer asked: {user_msg}. Answer politely in Bengali."
        
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        r = requests.post(url, headers=headers, json=data, timeout=15)
        res_json = r.json()
        
        if 'candidates' in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        elif 'error' in res_json:
            # যদি এখনও এরর দেয় তবে সরাসরি সেটি দেখাবে
            return f"❌ AI Error: {res_json['error']['message']}"
        else:
            return "🤖 AI এই মুহূর্তে উত্তর দিতে পারছে না।"
    except Exception as e:
        return f"⚠️ System Error: {str(e)}"

def handle_updates():
    """মেসেজ পড়া এবং উত্তর দেওয়া"""
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    try:
        response = requests.get(url).json()
        if response.get("ok") and response.get("result"):
            last_update_id = 0
            for update in response["result"]:
                last_update_id = update["update_id"]
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    user_text = update["message"]["text"]
                    
                    # AI থেকে স্মার্ট উত্তর নেওয়া
                    reply = get_ai_response(user_text)
                    
                    # কাস্টমারকে উত্তর পাঠানো
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                  json={"chat_id": chat_id, "text": reply})
            
            # পড়া মেসেজগুলো ক্লিয়ার করা
            requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id + 1}")
    except Exception as e:
        print(f"Telegram Error: {e}")

if __name__ == "__main__":
    if TOKEN:
        handle_updates()
