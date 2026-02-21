import os
import requests

# GitHub Secrets থেকে তথ্য নেওয়া
TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_response(user_msg):
    """Google Gemini AI ব্যবহার করে স্মার্ট উত্তর তৈরি করা"""
    if not GEMINI_API_KEY:
        return "❌ Error: GEMINI_API_KEY পাওয়া যাচ্ছে না। অনুগ্রহ করে GitHub Secrets চেক করুন।"

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        
        # আপনার বিজনেসের তথ্য এখানে দিন
        prompt = f"You are a professional Bengali assistant for 'Mintu Shop'. We sell Gadgets. Prices: Watch-500TK, Headphone-300TK. Customer asked: {user_msg}. Answer politely and briefly in Bengali."
        
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        r = requests.post(url, headers=headers, json=data, timeout=15)
        res_json = r.json()
        
        if 'candidates' in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        elif 'error' in res_json:
            return f"❌ AI Error: {res_json['error']['message']}"
        else:
            return "🤖 AI এই মুহূর্তে উত্তর দিতে পারছে না, কিছুক্ষণ পর চেষ্টা করুন।"
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
                    
                    print(f"মেসেজ পেয়েছেন: {user_text}")
                    reply = get_ai_response(user_text)
                    
                    # উত্তর পাঠানো
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                  json={"chat_id": chat_id, "text": reply})
            
            # পড়া মেসেজগুলো ক্লিয়ার করা যাতে বারবার উত্তর না আসে
            requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id + 1}")
        else:
            print("নতুন কোনো মেসেজ পাওয়া যায়নি।")
    except Exception as e:
        print(f"Telegram Error: {e}")

if __name__ == "__main__":
    if TOKEN:
        handle_updates()
    else:
        print("Error: BOT_TOKEN missing!")
