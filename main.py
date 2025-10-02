import os
from flask import Flask
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 7124683213

# Flask app for Render
app = Flask(__name__)

# Telegram bot
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID:
        await update.message.reply_text("✅ Hello Owner! Bot is active.")
    else:
        await update.message.reply_text("❌ You are not my owner!")

application.add_handler(CommandHandler("start", start))

# Flask route to keep alive
@app.route("/")
def index():
    return "Bot is running on Render!"

# Setup webhook
@app.before_first_request
def set_webhook():
    url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    asyncio.get_event_loop().create_task(bot.set_webhook(url))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
