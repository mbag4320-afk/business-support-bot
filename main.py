import os
import requests
import time

# GitHub Secrets থেকে তথ্য নেওয়া
TOKEN = os.getenv("BOT_TOKEN")
OWNER_CHAT_ID = os.getenv("CHAT_ID")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

def get_ai_response(user_msg):
    """Mistral AI ব্যবহার করে কাস্টমারের প্রশ্নের উত্তর দেওয়া"""
    if not MISTRAL_API_KEY: return "আমাদের সাথে যোগাযোগ করার জন্য ধন্যবাদ।"
    try:
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}
        
        # এখানে আপনার ব্যবসার তথ্য লিখে দিন
        system_info = "You are a helpful Bengali assistant for 'Mintu Shop'. We sell Gadgets. Prices: Watch-500TK, Headphone-300TK. If someone wants to order, ask for their address."
        
        data = {
            "model": "open-mistral-7b",
            "messages": [
                {"role": "system", "content": system_info},
                {"role": "user", "content": user_msg}
            ]
        }
        r = requests.post(url, headers=headers, json=data, timeout=15)
        return r.json()['choices'][0]['message']['content'].strip()
    except:
        return "দুঃখিত, আমাদের কাস্টমার কেয়ারে কল করুন: ০১৭XXXXXXXX"

def handle_updates():
    """মেসেজ চেক করা এবং উত্তর দেওয়া"""
    # শেষ কোন মেসেজটি প্রসেস করা হয়েছে তা চেক করতে (GitHub Actions এর জন্য সহজ পদ্ধতি)
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    updates = requests.get(url).json()
    
    if updates.get("result"):
        for update in updates["result"][-5:]: # শেষ ৫টি মেসেজ চেক করবে
            chat_id = update["message"]["chat"]["id"]
            user_text = update["message"]["text"]
            message_id = update["message"]["message_id"]

            # AI উত্তর তৈরি
            reply = get_ai_response(user_text)
            
            # কাস্টমারকে উত্তর পাঠানো
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                          json={"chat_id": chat_id, "text": reply})
            
            # যদি 'Order' শব্দ থাকে তবে আপনাকে (মালিককে) জানানো
            if "order" in user_text.lower() or "অর্ডার" in user_text:
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                              json={"chat_id": OWNER_CHAT_ID, 
                                    "text": f"🔔 নতুন অর্ডার এলার্ট!\nকাস্টমার আইডি: {chat_id}\nমেসেজ: {user_text}"})

if __name__ == "__main__":
    handle_updates()
