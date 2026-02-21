import os
import requests

TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_response(user_msg):
    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY is missing in GitHub Secrets!"

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        prompt = f"You are a helpful assistant for Mintu Shop. We sell Watch-500TK and Headphone-300TK. Customer asked: {user_msg}. Answer briefly in Bengali."
        
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        r = requests.post(url, headers=headers, json=data, timeout=15)
        res_json = r.json()
        
        # ডিবাগিং এর জন্য লগ প্রিন্ট করা
        print("Gemini API Response:", res_json)

        if 'candidates' in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        elif 'error' in res_json:
            return f"Gemini API Error: {res_json['error']['message']}"
        else:
            return "AI থেকে কোনো উত্তর পাওয়া যায়নি।"
    except Exception as e:
        return f"System Exception: {str(e)}"

def handle_updates():
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
            
            # মেসেজ ক্লিয়ার করা
            requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id + 1}")
    except Exception as e:
        print(f"Telegram Error: {e}")

if __name__ == "__main__":
    handle_updates()
