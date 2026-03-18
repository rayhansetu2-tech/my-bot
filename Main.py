import os
from flask import Flask
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Render-এর জন্য ওয়েব সার্ভার
server = Flask('')
@server.route('/')
def home(): return "Bot is Alive!"
def run(): server.run(host='0.0.0.0', port=8080)

# আপনার টোকেন
TOKEN = "8699071722:AAEuHjg6-rDnyrhssdNIERdBaicXz0qZaWU"

# মেনু ডিজাইন
main_menu = [
    [KeyboardButton("💰 Earn Money"), KeyboardButton("🎁 Daily Bonus")],
    [KeyboardButton("💳 Balance"), KeyboardButton("💸 Withdraw")],
    [KeyboardButton("👥 Refer & Earn"), KeyboardButton("📞 Support")]
]
markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏙 **Welcome to Set_Ai!**\n\nনিচের মেনু থেকে কাজ শুরু করুন।", reply_markup=markup, parse_mode='Markdown')

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "💰 Earn Money":
        await update.message.reply_text("📺 আপনার অ্যাড দেখার লিঙ্ক এখানে সেট করুন।")
    elif text == "💳 Balance":
        await update.message.reply_text("💰 আপনার ব্যালেন্স: ০ টাকা।")
    # এভাবে বাকি বাটনগুলো...

if __name__ == '__main__':
    Thread(target=run).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    app.run_polling()
  
