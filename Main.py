import sqlite3
import time
from threading import Thread
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# হোস্টিং সার্ভার (Render ২৪/৭ রাখার জন্য)
server = Flask('')
@server.route('/')
def home(): return "Bot is Online!"
def run(): server.run(host='0.0.0.0', port=8080)

# --- কনফিগারেশন (এগুলো আপনি চাইলে পাল্টাতে পারেন) ---
TOKEN = "8699071722:AAEuHjg6-rDnyrhssdNIERdBaicXz0qZaWU"
ADMIN_ID = 6853754984  # আপনার আইডি
CHANNEL_USER = "@your_channel" # আপনার পেমেন্ট চ্যানেল (ঐচ্ছিক)
DAILY_BONUS = 20
REFER_BONUS = 50
MIN_WITHDRAW = 500

# ডাটাবেস সেটআপ
db = sqlite3.connect('moneys_city_final.db', check_same_thread=False)
cursor = db.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (user_id INTEGER PRIMARY KEY, points REAL, last_bonus INTEGER, referred_by INTEGER)''')
db.commit()

# কিবোর্ড মেনু (ডিজাইন একদম আপনার মতো)
main_menu = [
    [KeyboardButton("💰 Earn Money"), KeyboardButton("🎁 Daily Bonus")],
    [KeyboardButton("💳 Balance"), KeyboardButton("💸 Withdraw")],
    [KeyboardButton("👥 Refer & Earn"), KeyboardButton("📊 Statistics")],
    [KeyboardButton("📞 Contact Admin")]
]
markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args # রেফারেল চেক
    
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        ref_id = int(args[0]) if args and args[0].isdigit() else None
        cursor.execute("INSERT INTO users VALUES (?, 0.0, 0, ?)", (user_id, ref_id))
        db.commit()
        if ref_id:
            cursor.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (REFER_BONUS, ref_id))
            db.commit()
            try: await context.bot.send_message(chat_id=ref_id, text=f"🎉 আপনার লিঙ্কে কেউ জয়েন করেছে! আপনি {REFER_BONUS} পয়েন্ট পেয়েছেন।")
            except: pass

    welcome_msg = f"🏙 **Welcome to {update.bot.first_name}!**\n\nনিচের বাটনগুলো চেপে ইনকাম করা শুরু করুন।"
    await update.message.reply_text(welcome_msg, reply_markup=markup, parse_mode='Markdown')

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    if not user: return

    if text == "💰 Earn Money":
        await update.message.reply_text("📺 **কাজ করতে নিচের লিঙ্কে যান:**\n\n(এখানে আপনার ভিডিও বা ওয়েবসাইট লিঙ্ক দিন)", reply_markup=markup)

    elif text == "🎁 Daily Bonus":
        now = int(time.time())
        if now - user[2] < 86400:
            await update.message.reply_text("❌ আপনি আজ বোনাস নিয়েছেন! ২৪ ঘণ্টা পর আবার ট্রাই করুন।")
        else:
            cursor.execute("UPDATE users SET points=points+?, last_bonus=? WHERE user_id=?", (DAILY_BONUS, now, user_id))
            db.commit()
            await update.message.reply_text(f"✅ অভিনন্দন! আপনি {DAILY_BONUS} পয়েন্ট বোনাস পেয়েছেন।")

    elif text == "💳 Balance":
        await update.message.reply_text(f"👤 **নাম:** {update.effective_user.first_name}\n💰 **ব্যালেন্স:** {user[1]} পয়েন্ট", parse_mode='Markdown')

    elif text == "💸 Withdraw":
        if user[1] < MIN_WITHDRAW:
            await update.message.reply_text(f"⚠️ টাকা তুলতে নূন্যতম {MIN_WITHDRAW} পয়েন্ট লাগবে।")
        else:
            await update.message.reply_text("📲 আপনার বিকাশ/নগদ নাম্বার এবং এমাউন্ট অ্যাডমিনকে পাঠান।")

    elif text == "👥 Refer & Earn":
        bot_username = (await context.bot.get_me()).username
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
        await update.message.reply_text(f"🔗 **আপনার রেফারেল লিঙ্ক:**\n{ref_link}\n\nপ্রতি রেফারে পাবেন {REFER_BONUS} পয়েন্ট!")

    elif text == "📊 Statistics":
        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]
        await update.message.reply_text(f"📊 **বট রিপোর্ট:**\n\n👥 মোট ইউজার: {total}\n✅ পেমেন্ট সচল আছে।")

    elif text == "📞 Contact Admin":
        await update.message.reply_text(f"💬 যেকোনো সমস্যায় যোগাযোগ করুন: [Admin ID](tg://user?id={ADMIN_ID})", parse_mode='Markdown')

if __name__ == '__main__':
    Thread(target=run).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    print("🚀 Final Bot is Running...")
    app.run_polling()
