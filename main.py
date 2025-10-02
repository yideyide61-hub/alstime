import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Get environment variables
TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 7124683213

if not TOKEN:
    raise ValueError("BOT_TOKEN not set!")

# Flask app
app = Flask(__name__)

# Telegram application
application = Application.builder().token(TOKEN).build()

# === Command Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID:
        await update.message.reply_text("✅ Hello Owner! Bot is active.")
    else:
        await update.message.reply_text("❌ You are not my owner!")

application.add_handler(CommandHandler("start", start))

# === Flask route for webhook ===
@app.route("/")
def index():
    return "Bot is running on Render!", 200

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok", 200

# === Set webhook before first request ===
@app.before_first_request
def set_webhook():
    url = f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/{TOKEN}"
    application.bot.set_webhook(url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
