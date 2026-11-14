import os
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_USERNAME = os.environ.get("BOT_USERNAME")

pending_referrals = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    if args:
        try:
            referrer_id = int(args[0])
            if referrer_id == user.id:
                await update.message.reply_text("Aap apne khud ke link par hain! Yeh link kisi aur ko bhejiye.")
                return

            button = KeyboardButton("📍 Apna Location Share Karein", request_location=True)
            reply_markup = ReplyKeyboardMarkup([[button]], one_time_keyboard=True, resize_keyboard=True)
            
            pending_referrals[user.id] = referrer_id
            await update.message.reply_text(
                "Hello! Aapke dost ne aapki location mangi hai. Apna location share karne ke liye neeche diye gaye button par click karein:",
                reply_markup=reply_markup
            )
        except ValueError:
            await update.message.reply_text("Invalid link!")
    else:
        await update.message.reply_text("Welcome! Apni tracking link banane ke liye /link command ka use karein.")

async def link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot_username = BOT_USERNAME or "Bot"
    link = f"https://t.me/{bot_username}?start={user.id}"
    await update.message.reply_text(f"Aapka tracking link yeh raha:\n\n{link}\n\nIsse apne doston ke sath share karein!")

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    location = update.message.location

    if user.id in pending_referrals:
        referrer_id = pending_referrals[user.id]
        try:
            await context.bot.send_location(
                chat_id=referrer_id,
                latitude=location.latitude,
                longitude=location.longitude
            )
            await update.message.reply_text("✅ Aapki location safalta-purvak bhej di gayi hai!")
            del pending_referrals[user.id]
        except Exception:
            await update.message.reply_text("Location bhejne mein kuch samasya aayi.")
    else:
        await update.message.reply_text("Dhanwaad!")

def main():
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN is missing!")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("link", link_command))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
