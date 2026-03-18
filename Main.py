import sqlite3
import time
from threading import Thread
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# হোস্টিং সার্ভার
server = Flask('')
@server.route('/')
def home(): return "Moneys City Bot is Live!"
def run(): server.run(host='0.0.0.0', port=8080)

# কনফিগারেশন
TOKEN = "8699071722:AAEuHjg6-rDnyrhssdNIERdBaicXz0qZaWU"
DAILY_BONUS_AMOUNT = 20

# ডাটাবেস
db = sqlite3.connect('moneys_city.db', check_same_thread=False)
cursor = db.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (user_id INTEGER PRIMARY KEY, points REAL, last_bonus INTEGER)''')
db.commit()

# মেনু ডিজাইন (হুবহু Moneys City-এর মতো)
main_menu = [
    [KeyboardButton("💰 Earn Money"), KeyboardButton("🎁 Daily Bonus")],
    [KeyboardButton("💳 Balance"), KeyboardButton("💸 Withdraw")],
    [KeyboardButton("📊 Statistics"), KeyboardButton("📞 Support")]
]
reply_markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (user_id, 0.0, 0))
        db.commit()
    
    welcome_text = (
        "🏙 **Welcome to Moneys City!**\n\n"
        "এখান থেকে আপনি প্রতিদিন অ্যাড দেখে ও রেফার করে টাকা আয় করতে পারবেন। "
        "নিচের বাটনগুলো ব্যবহার করে কাজ শুরু করুন।"
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if text == "💰 Earn Money":
        await update.message.reply_text("📺 **কাজ শুরু করতে নিচের বাটনটি চাপুন:**\n\n(এখানে আপনি আপনার অ্যাডের লিঙ্ক বা টাস্ক দিতে পারবেন।)", 
                                       reply_markup=reply_markup, parse_mode='Markdown')

    elif text == "🎁 Daily Bonus":
        now = int(time.time())
        if now - user[2] < 86400:
            await update.message.reply_text("❌ আপনি আজ বোনাস নিয়েছেন! ২৪ ঘণ্টা পর আবার আসুন।")
        else:
            cursor.execute("UPDATE users SET points=points+?, last_bonus=? WHERE user_id=?", (DAILY_BONUS_AMOUNT, now, user_id))
            db.commit()
            await update.message.reply_text(f"✅ অভিনন্দন! আপনি {DAILY_BONUS_AMOUNT} পয়েন্ট বোনাস পেয়েছেন।")

    elif text == "💳 Balance":
        await update.message.reply_text(f"👤 **ইউজার:** {update.effective_user.first_name}\n💰 **ব্যালেন্স:** {user[1]} পয়েন্ট", parse_mode='Markdown')

    elif text == "💸 Withdraw":
        await update.message.reply_text("⚠️ নূন্যতম ৫০০ পয়েন্ট হলে আপনি বিকাশ বা নগদে টাকা তুলতে পারবেন।")

    elif text == "📊 Statistics":
        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]
        await update.message.reply_text(f"📊 **বট পরিসংখ্যান:**\n👥 মোট ইউজার: {total}\n✅ পেমেন্ট সচল আছে।")

if __name__ == '__main__':
    Thread(target=run).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_messages))
    app.run_polling()
