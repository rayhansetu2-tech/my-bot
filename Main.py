import sqlite3
import time
from threading import Thread
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# হোস্টিং সার্ভার (Render ২৪/৭ সচল রাখার জন্য)
server = Flask('')
@server.route('/')
def home(): return "Bot is Online!"
def run(): server.run(host='0.0.0.0', port=8080)

# --- কনফিগারেশন ---
TOKEN = "8699071722:AAEuHjg6-rDnyrhssdNIERdBaicXz0qZaWU"
ADMIN_ID = 6853754984 
AD_LINK = "https://www.google.com" # এখানে আপনার অ্যাডের লিঙ্ক দিন
AD_REWARD = 5  # একটি অ্যাড দেখলে কত পয়েন্ট পাবে
REFER_REWARD = 50 # প্রতি রেফারে কত পাবে
MIN_WITHDRAW = 500

# ডাটাবেস সেটআপ
db = sqlite3.connect('moneys_city_new.db', check_same_thread=False)
cursor = db.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (user_id INTEGER PRIMARY KEY, points REAL, last_bonus INTEGER, referred_by INTEGER)''')
db.commit()

# প্রধান মেনু ডিজাইন (Statistics সরিয়ে দেওয়া হয়েছে)
main_menu = [
    [KeyboardButton("💰 Earn Money"), KeyboardButton("🎁 Daily Bonus")],
    [KeyboardButton("💳 Balance"), KeyboardButton("💸 Withdraw")],
    [KeyboardButton("👥 Refer & Earn"), KeyboardButton("📞 Support")]
]
markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args 
    
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        ref_id = int(args[0]) if args and args[0].isdigit() else None
        cursor.execute("INSERT INTO users VALUES (?, 0.0, 0, ?)", (user_id, ref_id))
        db.commit()
        if ref_id:
            try: await context.bot.send_message(chat_id=ref_id, text="🎉 কেউ আপনার লিঙ্কে জয়েন করেছে! সে কাজ শুরু করলে আপনি বোনাস পাবেন।")
            except: pass

    await update.message.reply_text(f"🏙 **Welcome to {update.bot.first_name}!**\n\nকাজ শুরু করতে নিচের বাটন চাপুন।", reply_markup=markup, parse_mode='Markdown')

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    cursor.execute("SELECT points, last_bonus FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    if not user: return

    if text == "💰 Earn Money":
        # অ্যাড দেখার ইনলাইন বাটন
        keyboard = [
            [InlineKeyboardButton("📺 Watch Video Ad", url=AD_LINK)],
            [InlineKeyboardButton("✅ Claim Reward", callback_data="claim_ad")]
        ]
        await update.message.reply_text(
            "🎁 **অ্যাড দেখে ইনকাম করুন:**\n\nনিচের বাটনে ক্লিক করে অ্যাডটি দেখুন, তারপর 'Claim Reward' বাটনে ক্লিক করুন।",
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown'
        )

    elif text == "🎁 Daily Bonus":
        now = int(time.time())
        if now - user[1] < 86400:
            await update.message.reply_text("❌ আপনি আজ বোনাস নিয়েছেন! ২৪ ঘণ্টা পর আবার আসুন।")
        else:
            cursor.execute("UPDATE users SET points=points+20, last_bonus=? WHERE user_id=?", (now, user_id))
            db.commit()
            await update.message.reply_text("✅ অভিনন্দন! আপনি ২০ পয়েন্ট বোনাস পেয়েছেন।")

    elif text == "💳 Balance":
        await update.message.reply_text(f"💰 **আপনার বর্তমান ব্যালেন্স:** {user[0]} পয়েন্ট", parse_mode='Markdown')

    elif text == "👥 Refer & Earn":
        bot_username = (await context.bot.get_me()).username
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
        await update.message.reply_text(
            f"👥 **রেফার করে আয় করুন!**\n\nআপনার বন্ধুদের ইনভাইট করুন। প্রতি রেফারে পাবেন {REFER_REWARD} পয়েন্ট!\n\n🔗 **আপনার লিঙ্ক:**\n{ref_link}",
            parse_mode='Markdown'
        )

    elif text == "💸 Withdraw":
        await update.message.reply_text(f"⚠️ নূন্যতম {MIN_WITHDRAW} পয়েন্ট হলে উইথড্র করতে পারবেন। আপনার বিকাশ/নগদ নম্বর অ্যাডমিনকে জানান।")

    elif text == "📞 Support":
        await update.message.reply_text(f"💬 সরাসরি অ্যাডমিনের সাথে কথা বলুন: [Admin ID](tg://user?id={ADMIN_ID})", parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if query.data == "claim_ad":
        cursor.execute("UPDATE users SET points=points+? WHERE user_id=?", (AD_REWARD, user_id))
        db.commit()
        await query.answer("✅ আপনি ৫ পয়েন্ট পেয়েছেন!")
        await query.edit_message_text("✅ আপনার রিওয়ার্ড যোগ করা হয়েছে। পরবর্তী অ্যাডের জন্য আবার চেষ্টা করুন।")

if __name__ == '__main__':
    Thread(target=run).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.run_polling()
  
