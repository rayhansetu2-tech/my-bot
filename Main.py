import sqlite3
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8699071722:AAEuHjg6-rDnyrhssdNIERdBaicXz0qZaWU"

# বাটনগুলো এখানে ডিফাইন করা হয়েছে
main_menu = [
    [KeyboardButton("💰 Earn Money"), KeyboardButton("🎁 Daily Bonus")],
    [KeyboardButton("💳 Balance"), KeyboardButton("💸 Withdraw")],
    [KeyboardButton("👥 Refer & Earn"), KeyboardButton("📞 Support")]
]
markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # এই মেসেজটি দিলেই বাটনগুলো মোবাইলে ভেসে উঠবে
    await update.message.reply_text("🏙 **Welcome!**\nকাজ শুরু করতে নিচের বাটন চাপুন।", reply_markup=markup, parse_mode='Markdown')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
    
