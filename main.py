import os
import requests
import time

# এখানে আপনার তথ্যগুলো বসান
TOKEN = "আপনার_টেলিগ্রাম_বট_টোকেন"
GEMINI_API_KEY = "AIzaSyARc-IoUyygjHTjr5xytu5HeNCZk21Q9vg" # মিস্ট্রালের বদলে জেমিনি কী দিন

def get_ai_response(user_msg):
    """Google Gemini AI ব্যবহার করে উত্তর দেওয়া"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        
        # আপনার দোকানের তথ্য এখানে দিন
        prompt = f"You are a helpful Bengali assistant for 'Mintu Shop'. We sell Watch-500TK, Headphone-300TK. Customer asked: {user_msg}. Answer in Bengali briefly."
        
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        r = requests.post(url, headers=headers, json=data, timeout=15)
        result = r.json()
        
        i
