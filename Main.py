import sqlite3
import time
import random
from threading import Thread
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# হোস্টিং সার্ভার (Render-এ ২৪ ঘণ্টা চালানোর জন্য)
server = Flask('')
@server.route('/')
def home(): return "Moneys City Bot is Active!"
def run(): server.run(host='0.0.0.0', port=8080)

# বটের কনফিগারেশন
TOKEN = "8699071722:AAEuHjg6-rDnyrhssdNIERdBaicXz0qZaWU"
ADMIN_ID = 6853754984 

# ডাটাবেস সেটআপ
db = sqlite3.connect('moneys_city.db', check_same_thread=False)
cursor = db.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (user_id INTEGER PRIMARY KEY, points REAL, last_bonus INTEGER)''')
db.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (user_id, 0.0, 0))
        db.commit()
    
    menu = [['💰 Earn Money', '🎁 Daily Bonus'], ['💳 Balance', '💸 Withdraw']]
    await update.message.reply_text("🏙 **Welcome to Moneys City!**", 
                                   reply_markup=ReplyKeyboardMarkup(menu, resize_keyboard=True))

if __name__ == '__main__':
    Thread(target=run).start() # সার্ভার চালু
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("🚀 Bot is running...")
    app.run_polling()
