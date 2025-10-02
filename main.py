import os
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN", "8466271055:AAEuITQNe4DXvSX2GFybR0oB-2cPmnc6Hs8")
OWNER_ID = 7124683213

# Flask app (for Render health check)
app = Flask(__name__)

@app.route("/")
def index():
    return "✅ Bot is running on Render!"

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID:
        await update.message.reply_text("✅ Hello Owner! Bot is active.")
    else:
        await update.message.reply_text("❌ You are not my owner!")

def main():
    # Build application
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))

    # Webhook settings
    port = int(os.environ.get("PORT", 10000))
    render_hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    webhook_url = f"https://{render_hostname}/{TOKEN}"

    # Run webhook (async server built-in)
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TOKEN,
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    main()
