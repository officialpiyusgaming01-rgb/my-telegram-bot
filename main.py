
        
import telebot
from telebot import types
import json
import os
import time
from threading import Thread
from flask import Flask

# 1. Flask Web Server Setup (Render ke liye zaroori)
app = Flask('')

@app.route('/')
def home():
    return "Bot is active 24/7 on Render!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web_server)
    t.daemon = True
    t.start()

# 2. Main Telegram Bot Setup
BOT_TOKEN = "8797130773:AAHAYSlvwjRZP-TqR1bmaG7KXnbO4_cndTE"
bot = telebot.TeleBot(BOT_TOKEN, num_threads=4)

# 📢 Aapke Dono Channels Yahan Set Hain
CHANNEL_1 = "@profits_app" 
CHANNEL_2 = "@modp_apk" 

ADMIN_ID = 7013666151  # Aapki asli Admin ID
DB_FILE = "database.json"

# Database Helper Functions
def load_data():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Dono channels ki membership strictly check karega
def is_user_subscribed(user_id):
    try:
        member1 = bot.get_chat_member(CHANNEL_1, user_id)
        is_joined1 = member1.status in ['member', 'creator', 'administrator']
        
        member2 = bot.get_chat_member(CHANNEL_2, user_id)
        is_joined2 = member2.status in ['member', 'creator', 'administrator']
        
        return is_joined1 and is_joined2
    except Exception as e:
        print(f"❌ Channel Check Error: {e}")
        return False 

# 🛠️ Main Menu UI (YouTube Shorts Link Button Ke Saat)
def show_main_menu(user_id, user_name):
    markup = types.InlineKeyboardMarkup()
    
    # 🔗 Aapka YouTube Shorts Video Link
    shorts_url = "https://youtube.com/shorts/J1HZ9GQiJRc?si=QC0YRtkIJDNbdl2E"
    
    # Video open karne wala button (Is par click karte hi video khulegi)
    btn_video = types.InlineKeyboardButton("📺 Watch New Video", url=shorts_url)
    
    markup.add(btn_video)
    
    bot.send_message(
        user_id, 
        f"👋 Namaste {user_name}!\n\nWelcome back to PIYUS GAMING Bot. Aapka account active hai.\n\n👇 Neeche diye gaye button par click karke hamari trending video dekhein:", 
        reply_markup=markup
    )

# /start Command Handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        user_id = str(message.chat.id)
        user_name = message.from_user.first_name
        
        db = load_data()
        if user_id not in db:
            db[user_id] = {"name": user_name, "coins": 100}
            save_data(db)
            
        if not is_user_subscribed(message.chat.id):
            markup = types.InlineKeyboardMarkup()
            
            btn_join1 = types.InlineKeyboardButton("📢 Join Channel 1", url="https://t.me/profits_app")
            btn_join2 = types.InlineKeyboardButton("📢 Join Channel 2", url="https://t.me/modp_apk")
            btn_refresh = types.InlineKeyboardButton("🔄 Maine Dono Join Kar Liya", callback_data="check_again")
            
            markup.add(btn_join1)
            markup.add(btn_join2)
            markup.add(btn_refresh)
            
            bot.send_message(
                user_id, 
                f"⚠️ Hey {user_name}! Access Denied\n\n"
                f"Is bot ko use karne ke liye aapko hamare DONO official channels ko join karna zaroori hai.\n\n"
                f"👇 Neeche dono buttons par click karke join kejiye:", 
                reply_markup=markup
            )
            return 
            
        show_main_menu(user_id, user_name)
    except Exception as e:
        print(f"Error in start: {e}")

# Inline Buttons Click Listener
@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
