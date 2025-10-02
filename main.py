import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, ChatMemberHandler, ContextTypes

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# === CONFIG ===
BOT_OWNER_ID = 7124683213   # your Telegram ID
TOKEN = "8466271055:AAEuITQNe4DXvSX2GFybR0oB-2cPmnc6Hs8"

# Flask app
app = Flask(__name__)

# Telegram bot application
application = Application.builder().token(TOKEN).build()

# === Handler: check who added bot ===
async def check_who_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = update.my_chat_member
    if member.new_chat_member.user.id == context.bot.id:
        chat_id = member.chat.id
        adder = member.from_user
        chat_title = member.chat.title if member.chat.title else "Private Chat"

        logger.info(f"✅ Bot added to group: {chat_title} (id={chat_id})")
        logger.info(f"👤 Added by: {adder.full_name} (id={adder.id}, username=@{adder.username})")

        if adder.id == BOT_OWNER_ID:
            await context.bot.send_message(chat_id, "🤖 Bot added by my owner. Ready to work!")
        else:
            await context.bot.send_message(chat_id, "⛔ Only my owner can add me. Leaving...")
            await context.bot.leave_chat(chat_id)

# Register handler
application.add_handler(ChatMemberHandler(check_who_added, ChatMemberHandler.MY_CHAT_MEMBER))

# === Webhook endpoint ===
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok", 200

@app.route("/")
def home():
    return "Bot is running on Render!", 200

# Run with webhook
if __name__ == "__main__":
    import asyncio
    from telegram import Bot

    bot = Bot(TOKEN)

    # Set webhook (Render gives us PORT + HOST)
    url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    asyncio.run(bot.set_webhook(url=url))

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
