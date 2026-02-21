import os
import requests

# GitHub Secrets থেকে তথ্য নেওয়া
TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("AIzaSyARc-IoUyygjHTjr5xytu5HeNCZk21Q9vg")

def get_ai_response(user_msg):
    """Google Gemini AI ব্যবহার করে স্মার্ট উত্তর তৈরি করা"""
    if not GEMINI_API_KEY:
        return "Error: Gemini API Key missing in GitHub Secrets!"

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        # আপনার বিজনেসের তথ্য এখানে দিন
        prompt = f"You are a helpful Bengali assistant for Mintu Shop. We sell Watch (500 TK) and Headphones (300 TK). Customer asked: {user_msg}. Answer politely in Bengali."
        
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        r = requests.post(url, headers=headers, json=data, timeout=15)
        
        res_json = r.json()
        if 'candidates' in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            return f"AI Error: {res_json.get('error', {}).get('message', 'Unknown error')}"
    except Exception as e:
        return f"System Error: {str(e)}"

def handle_updates():
    """মেসেজ পড়া এবং উত্তর দেওয়া"""
    # গেট আপডেট
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    updates = requests.get(url).json()
    
    if updates.get("ok") and updates.get("result"):
        last_update_id = 0
        for update in updates["result"]:
            last_update_id = update["update_id"]
            if "message" in update and "text" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                user_text = update["message"]["text"]
                
                print(f"Processing message: {user_text}")
                
                # AI থেকে উত্তর নেওয়া
                reply = get_ai_response(user_text)
                
                # কাস্টমারকে উত্তর পাঠানো
                send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                requests.post(send_url, json={"chat_id": chat_id, "text": reply})
        
        # মেসেজগুলো 'পড়া হয়েছে' হিসেবে মার্ক করা যাতে পরের বার ডুপ্লিকেট না আসে
        requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id + 1}")

if __name__ == "__main__":
    if TOKEN:
        handle_updates()
    else:
        print("Error: BOT_TOKEN is missing!")
