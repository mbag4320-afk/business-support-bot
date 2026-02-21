import os
import requests

# GitHub Secrets থেকে তথ্য নেওয়া
TOKEN = os.getenv("BOT_TOKEN")
OWNER_CHAT_ID = os.getenv("CHAT_ID")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

def get_ai_response(user_msg):
    """Mistral AI ব্যবহার করে কাস্টমারের প্রশ্নের স্মার্ট উত্তর দেওয়া"""
    if not MISTRAL_API_KEY:
        return "Error: MISTRAL_API_KEY পাওয়া যাচ্ছে না।"

    try:
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {MISTRAL_API_KEY}"
        }
        
        # আপনার দোকানের তথ্য এখানে দিন
        system_info = (
            "You are a helpful Bengali assistant for 'Mintu Shop'. "
            "We sell: Watch (500 TK), Headphones (300 TK), and Smart Gadgets. "
            "Be polite. If someone wants to order, ask for their delivery address. "
            "Answer briefly in Bengali."
        )
        
        data = {
            "model": "open-mistral-7b",
            "messages": [
                {"role": "system", "content": system_info},
                {"role": "user", "content": user_msg}
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=15)
        res_json = response.json()
        
        if 'choices' in res_json:
            return res_json['choices'][0]['message']['content'].strip()
        else:
            return "ধন্যবাদ, আমরা শীঘ্রই আপনার সাথে যোগাযোগ করব।"
    except Exception as e:
        print(f"AI Error: {e}")
        return "দুঃখিত, আমাদের সার্ভারে সমস্যা হচ্ছে। অনুগ্রহ করে পরে চেষ্টা করুন।"

def handle_updates():
    """টেলিগ্রাম থেকে মেসেজ পড়া এবং উত্তর দেওয়া"""
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
                    
                    # AI থেকে উত্তর তৈরি করা
                    reply = get_ai_response(user_text)
                    
                    # কাস্টমারকে উত্তর পাঠানো
                    send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                    requests.post(send_url, json={"chat_id": chat_id, "text": reply})
                    
                    # যদি কেউ 'অর্ডার' করতে চায়, আপনাকে (মালিককে) নোটিফিকেশন দেবে
                    if "order" in user_text.lower() or "অর্ডার" in user_text:
                        requests.post(send_url, json={
                            "chat_id": OWNER_CHAT_ID, 
                            "text": f"🔔 নতুন অর্ডার এলার্ট!\nকাস্টমার আইডি: {chat_id}\nমেসেজ: {user_text}"
                        })
            
            # মেসেজগুলো 'পড়া হয়েছে' হিসেবে মার্ক করা যাতে বারবার একই উত্তর না আসে
            requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id + 1}")
        else:
            print("নতুন কোনো মেসেজ পাওয়া যায়নি।")
    except Exception as e:
        print(f"Telegram Error: {e}")

if __name__ == "__main__":
    if TOKEN:
        handle_updates()
    else:
        print("Error: BOT_TOKEN is missing!")
