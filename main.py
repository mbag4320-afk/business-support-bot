import os
import requests

# GitHub Secrets থেকে তথ্য নেওয়া
TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_response(user_msg):
    """গুগলের একাধিক মডেল ট্রাই করার স্মার্ট লজিক"""
    if not GEMINI_API_KEY:
        return "❌ Error: GEMINI_API_KEY পাওয়া যাচ্ছে না।"

    # যে মডেলগুলো আমরা ট্রাই করব
    models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]
    
    last_error = ""
    
    for model_name in models:
        try:
            # v1beta এবং v1 উভয় ভার্সনেই ট্রাই করবে
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
            headers = {'Content-Type': 'application/json'}
            
            prompt = f"You are a helpful Bengali assistant for Mintu Shop. We sell Watch (500 TK) and Headphones (300 TK). Customer asked: {user_msg}. Answer politely in Bengali."
            
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            r = requests.post(url, headers=headers, json=data, timeout=15)
            res_json = r.json()
            
            if 'candidates' in res_json:
                return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
            elif 'error' in res_json:
                last_error = res_json['error']['message']
                continue # পরের মডেল ট্রাই করবে
        except Exception as e:
            last_error = str(e)
            continue

    return f"❌ AI Error: সব মডেল ট্রাই করা হয়েছে কিন্তু কাজ করছে না। সর্বশেষ এরর: {last_error}"

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
                    
                    # স্মার্ট এআই উত্তর
                    reply = get_ai_response(user_text)
                    
                    # টেলিগ্রামে পাঠানো
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                  json={"chat_id": chat_id, "text": reply})
            
            # মেসেজ ক্লিয়ার করা
            requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id + 1}")
    except Exception as e:
        print(f"Telegram Error: {e}")

if __name__ == "__main__":
    if TOKEN:
        handle_updates()
