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

CHANNEL_USERNAME = "@profits_app" 
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

# Strictly check karega channel membership
def is_user_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'creator', 'administrator']:
            return True
        return False
    except Exception as e:
        print(f"❌ Channel Check Error: {e}")
        return False 

# Main Menu UI
def show_main_menu(user_id, user_name):
    markup = types.InlineKeyboardMarkup()
    btn_wallet = types.InlineKeyboardButton("💰 My Wallet", callback_data="check_wallet")
    markup.add(btn_wallet)
    bot.send_message(user_id, f"👋 **Namaste {user_name}!**\n\nWelcome back to PIYUS GAMING Bot. Aapka account active hai.", reply_markup=markup)

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
            
        # Naya aur Aacha Message Layout (Force Join)
        if not is_user_subscribed(message.chat.id):
            markup = types.InlineKeyboardMarkup()
            btn_join = types.InlineKeyboardButton("📢 Join Channel", url="https://t.me/profits_app")
            btn_refresh = types.InlineKeyboardButton("🔄 Maine Join Kar Liya", callback_data="check_again")
            markup.add(btn_join, btn_refresh)
            
            # Yahan maine aapka text mast change kar diya hai:
            bot.send_message(
                user_id, 
                f"⚠️ **Hey {user_name}! Access Denied**\n\n"
                f"Is bot ke premium features aur coins wallet use karne ke liye, "
                f"aapko hamare **Official Telegram Channel** ko join karna zaroori hai.\n\n"
                f"👇 **Neeche button par click karke join karein:**", 
                reply_markup=markup
            )
            return 
            
        show_main_menu(user_id, user_name)
    except Exception as e:
        print(f"Error in start: {e}")

# Inline Buttons Click Listener
@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    try:
        user_id = str(call.message.chat.id)
        user_name = call.from_user.first_name
        db = load_data()
        
        if call.data == "check_wallet":
            user_coins = db.get(user_id, {}).get("coins", 0)
            bot.send_message(user_id, f"💳 **Aapka Wallet Balance:**\n\n💰 Coins: {user_coins} Coins\n🆔 Your ID: `{user_id}`")
            bot.answer_callback_query(call.id)
            
        elif call.data == "check_again":
            if is_user_subscribed(int(user_id)):
                bot.answer_callback_query(call.id, "✅ Thank you join karne ke liye!")
                show_main_menu(user_id, user_name)
            else:
                bot.answer_callback_query(call.id, "❌ Aapne abhi tak join nahi kiya hai!", show_alert=True)
    except Exception as e:
        print(f"Callback Error: {e}")

# Admin Command: /addcoins USER_ID COINS
@bot.message_handler(commands=['addcoins'])
def add_coins_admin(message):
    try:
        if message.chat.id != ADMIN_ID:
            bot.reply_to(message, "❌ Aap is bot ke admin nahi hain!")
            return
            
        text = message.text.split()
        if len(text) != 3:
            bot.reply_to(message, "⚠️ Sahi format: `/addcoins USER_ID COINS` \n\nExample: `/addcoins 7013666151 500`")
            return
            
        target_id = text[1]
        coins_to_add = int(text[2])
        
        db = load_data()
        if target_id in db:
            db[target_id]["coins"] += coins_to_add
            save_data(db)
            bot.reply_to(message, f"✅ Done! ID {target_id} me {coins_to_add} coins add ho gaye.")
            bot.send_message(int(target_id), f"🎁 **Admin ne aapke wallet me {coins_to_add} Coins add kiye hain!**")
        else:
            bot.reply_to(message, "❌ Yeh User ID database me nahi mila!")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

# Web server start
keep_alive()
print("🚀 Render Highly-Optimized Bot Live!")

bot.remove_webhook()
time.sleep(1)

while True:
    try:
        bot.polling(none_stop=True, timeout=5, long_polling_timeout=5)
    except Exception as e:
        time.sleep(3)
        
