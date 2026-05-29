import telebot
from telebot import types
import json
import os
import time
import random
from threading import Thread
from flask import Flask

# 1. Flask Web Server Setup (Render ke liye)
app = Flask('')
@app.route('/')
def home(): 
    return "Ultimate Bot is active 24/7!"

def run_web_server(): 
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

Thread(target=run_web_server, daemon=True).start()

# 2. Main Telegram Bot Setup
BOT_TOKEN = "8797130773:AAHAYSlvwjRZP-TqR1bmaG7KXnbO4_cndTE"
bot = telebot.TeleBot(BOT_TOKEN, num_threads=4)

CHANNEL_1 = "@profits_app" 
CHANNEL_2 = "@modp_apk" 
ADMIN_ID = 7013666151  # Aapki Admin ID
DB_FILE = "database.json"

# Database Helpers
def load_data():
    if not os.path.exists(DB_FILE): return {}
    with open(DB_FILE, "r") as f: return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

# Channel Join Check
def is_user_subscribed(user_id):
    try:
        m1 = bot.get_chat_member(CHANNEL_1, user_id).status in ['member', 'creator', 'administrator']
        m2 = bot.get_chat_member(CHANNEL_2, user_id).status in ['member', 'creator', 'administrator']
        return m1 and m2
    except: return False

# Main Menu UI (All Features Fixed)
def show_main_menu(user_id, user_name):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_watch = types.InlineKeyboardButton("📺 Watch & Earn", callback_data="watch_video")
    btn_bonus = types.InlineKeyboardButton("🎁 Daily Bonus", callback_data="daily_bonus")
    btn_spin = types.InlineKeyboardButton("🎡 Spin Wheel", callback_data="spin_wheel")
    btn_refer = types.InlineKeyboardButton("👥 Refer & Earn", callback_data="refer_earn")
    btn_balance = types.InlineKeyboardButton("💰 My Balance", callback_data="check_balance")
    btn_store = types.InlineKeyboardButton("🛒 Redeem Store", callback_data="open_store")
    
    markup.add(btn_watch, btn_bonus)
    markup.add(btn_spin, btn_refer)
    markup.add(btn_balance, btn_store)
    
    bot.send_message(
        user_id, 
        f"👋 **Namaste {user_name}!**\n\n"
        f"Welcome to **PIYUS GAMING Ultimate Earning Bot**! 🎉\n\n"
        f"Neeche diye gaye tariko se coins kamayein aur Free Fire Diamonds ya Paytm Cash redeem karo! 🔥", 
        reply_markup=markup
    )

# /start Command Handler (With Refer Tracking)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        user_id = str(message.chat.id)
        user_name = message.from_user.first_name
        text = message.text.split()
        
        db = load_data()
        
        # Naya User Registration
        is_new_user = False
        if user_id not in db:
            is_new_user = True
            db[user_id] = {
                "name": user_name, 
                "coins": 100, 
                "watched_today": False, 
                "last_bonus": 0, 
                "spins_left": 3, 
                "last_spin_reset": time.time(),
                "referred_by": None
            }
            # Refer Code Track Karen
            if len(text) > 1 and text[1].isdigit() and text[1] != user_id:
                db[user_id]["referred_by"] = text[1]
            save_data(db)
            
        # Membership Strict Check
        if not is_user_subscribed(message.chat.id):
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📢 Join Channel 1", url="https://t.me/profits_app"))
            markup.add(types.InlineKeyboardButton("📢 Join Channel 2", url="https://t.me/modp_apk"))
            markup.add(types.InlineKeyboardButton("🔄 Maine Dono Join Kar Liya", callback_data="check_again"))
            
            bot.send_message(
                user_id, 
                f"⚠️ **Hey {user_name}! Access Denied**\n\n"
                f"Is bot ko use karne ke liye aapko hamare **DONO** official channels ko join karna zaroori hai.\n\n"
                f"👇 **Neeche dono buttons par click karke join kejiye:**", 
                reply_markup=markup
            )
            return 
            
        # Refer reward process
        if is_new_user and db[user_id]["referred_by"]:
            referrer = db[user_id]["referred_by"]
            if referrer in db:
                db[referrer]["coins"] += 50
                save_data(db)
                try: bot.send_message(int(referrer), f"👥 **Refer Alert!** Aapke link se {user_name} ne bot join kiya. Aapko **50 Coins** mile! 🎉")
                except: pass
                db[user_id]["referred_by"] = None
                save_data(db)

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
        
        # 1. Watch Video
        if call.data == "watch_video":
            markup = types.InlineKeyboardMarkup()
            btn_link = types.InlineKeyboardButton("▶️ Open YouTube Video", url="https://youtube.com/shorts/J1HZ9GQiJRc?si=7u81ylMVnJ53aXHt")
            btn_claim = types.InlineKeyboardButton("🎁 Claim Reward (20 Coins)", callback_data="claim_coins")
            markup.add(btn_link, btn_claim)
            bot.send_message(user_id, "📺 **Video dekh kar kamao!**\n\nShorts video ko pura dekhne ke baad hi Claim button dabayein.", reply_markup=markup)
            bot.answer_callback_query(call.id)
            
        elif call.data == "claim_coins":
            if db.get(user_id, {}).get("watched_today", False):
                bot.answer_callback_query(call.id, "❌ Aapne yeh video aaj pehle hi dekh liya hai!", show_alert=True)
            else:
                db[user_id]["coins"] += 20
                db[user_id]["watched_today"] = True
                save_data(db)
                bot.send_message(user_id, "✅ **Mubarak Ho!** Aapko **20 Coins** mil gaye hain! 🎉")
                bot.answer_callback_query(call.id)
                
        # 2. Daily Bonus
        elif call.data == "daily_bonus":
            current_time = time.time()
            last_bonus = db.get(user_id, {}).get("last_bonus", 0)
            if current_time - last_bonus < 86400:
                time_passed = current_time - last_bonus
                hours_left = int((86400 - time_passed) // 3600)
                bot.answer_callback_query(call.id, f"❌ Aap apna aaj ka bonus le chuke hain! agle {hours_left} ghante baad aana.", show_alert=True)
            else:
                db[user_id]["coins"] += 50
                db[user_id]["last_bonus"] = current_time
                save_data(db)
                bot.send_message(user_id, "🎁 **Daily Bonus Claimed!** Aapke wallet mein **50 Coins** jod diye gaye hain.")
                bot.answer_callback_query(call.id)

        # 3. Spin Wheel
        elif call.data == "spin_wheel":
            current_time = time.time()
            last_reset = db.get(user_id, {}).get("last_spin_reset", 0)
            
            if current_time - last_reset > 86400:
                db[user_id]["spins_left"] = 3
                db[user_id]["last_spin_reset"] = current_time
                save_data(db)
                
            spins_left = db[user_id].get("spins_left", 3)
            if spins_left <= 0:
                bot.answer_callback_query(call.id, "❌ Aapke aaj ke saare 3 spins poore ho gaye hain! Kal fir aana.", show_alert=True)
            else:
                prizes = [0, 10, 20, 50, 10, 20]
                win = random.choice(prizes)
                db[user_id]["coins"] += win
                db[user_id]["spins_left"] -= 1
                save_data(db)
                bot.send_message(user_id, f"🎡 **Spinnnn... 🎯**\n\nMubarak Ho! Aapko pahiya ghumane par **{win} Coins** mile! 🎉\n(Aapke pass aaj ke {db[user_id]['spins_left']} spins bache hain)")
                bot.answer_callback_query(call.id)

        # 4. Refer & Earn
        elif call.data == "refer_earn":
            bot_info = bot.get_me()
            refer_link = f"https://t.me/{bot_info.username}?start={user_id}"
            bot.send_message(
                user_id, 
                f"👥 **Refer & Earn System** 👥\n\n"
                f"Apne doston ko bot join karwayein aur dheron coins kamayein!\n\n"
                f"🎁 **Per Refer Reward:** 50 Coins\n\n"
                f"🔗 **Aapka Personal Invite Link:**\n`{refer_link}`\n\n"
                f"*(Isko copy karke doston ko share karein)*"
            )
            bot.answer_callback_query(call.id)

        # 5. Check Balance
        elif call.data == "check_balance":
            user_coins = db.get(user_id, {}).get("coins", 100)
            bot.send_message(user_id, f"💳 **Aapka Wallet Balance:**\n\n💰 Coins: {user_coins} Coins\n🆔 Your ID: `{user_id}`")
            bot.answer_callback_query(call.id)

        # 6. Redeem Store
        elif call.data == "open_store":
            markup = types.InlineKeyboardMarkup()
            btn_ff = types.InlineKeyboardButton("🎮 50 FF Diamonds (2000 Coins)", callback_data="redeem_ff")
            btn_paytm = types.InlineKeyboardButton("💸 20 Rs Paytm Cash (1000 Coins)", callback_data="redeem_paytm")
            markup.add(btn_ff, btn_paytm)
            bot.send_message(user_id, "🛒 **PIYUS GAMING Redeem Store**\n\nApna reward select karein:", reply_markup=markup)
            bot.answer_callback_query(call.id)

        elif call.data in ["redeem_ff", "redeem_paytm"]:
            user_coins = db.get(user_id, {}).get("coins", 100)
            required = 2000 if call.data == "redeem_ff" else 1000
            item_name = "50 Free Fire Diamonds" if call.data == "redeem_ff" else "20 Rs Paytm Cash"
            
            if user_coins < required:
                bot.answer_callback_query(call.id, f"❌ Aapke paas kaafi coins nahi hain! Iske liye {required} coins chahiye.", show_alert=True)
            else:
                bot.answer_callback_query(call.id)
                msg = bot.send_message(user_id, f"📝 **Redeem Details:**\n\nAap **{item_name}** redeem kar rahe hain.\n\nKripya apna **Free Fire UID** ya **Paytm Number** yahan message type karke bhejein:")
                bot.register_next_step_handler(msg, process_redeem, required, item_name)

        # Verify channels again
        elif call.data == "check_again":
            if is_user_subscribed(int(user_id)):
                bot.answer_callback_query(call.id, "✅ Verification Successful!")
                show_main_menu(user_id, user_name)
            else:
                bot.answer_callback_query(call.id, "❌ Aapne abhi tak dono channels join nahi kiye hain!", show_alert=True)
    except Exception as e:
        print(f"Callback Error: {e}")

# Process Redeem Requests
def process_redeem(message, cost, item_name):
    try:
        user_id = str(message.chat.id)
        user_name = message.from_user.first_name
        user_input = message.text
        db = load_data()
        
        if db.get(user_id, {}).get("coins", 100) < cost:
            bot.send_message(user_id, "❌ Error! Coins kam hain.")
            return
            
        db[user_id]["coins"] -= cost
        save_data(db)
        
        bot.send_message(user_id, f"✅ **Redeem Request Received!**\n\nItem: {item_name}\nDetails: `{user_input}`\n\nAdmin 24 ghante ke andar check karke reward bhej denge! 👍")
        
        # Admin Alert Notification 📢
        admin_msg = (
            f"🚨 **NEW REDEEM REQUEST** 🚨\n\n"
            f"👤 **User:** {user_name}\n"
            f"🆔 **Telegram ID:** `{user_id}`\n"
            f"🎁 **Reward:** {item_name}\n"
            f"📝 **User Input UID/No:** `{user_input}`"
        )
        bot.send_message(ADMIN_ID, admin_msg)
    except Exception as e:
        print(f"Redeem Error: {e}")

# Admin Command: /addcoins USER_ID COINS
@bot.message_handler(commands=['addcoins'])
def add_coins_admin(message):
    try:
        if message.chat.id != ADMIN_ID: return
        text = message.text.split()
        if len(text) != 3: return
        target_id, coins_to_add = text[1], int(text[2])
        db = load_data()
        if target_id in db:
            db[target_id]["coins"] += coins_to_add
            save_data(db)
            bot.reply_to(message, "✅ Coins added successfully!")
            bot.send_message(int(target_id), f"🎁 **Admin ne aapko {coins_to_add} Coins diye hain!**")
    except Exception as e: print(e)

bot.remove_webhook()
time.sleep(1)

while True:
    try: bot.polling(none_stop=True, timeout=5, long_polling_timeout=5)
    except Exception as e: time.sleep(3)
        
