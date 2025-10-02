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

# Environment variables
BOT_OWNER_ID = 7124683213   # your Telegram ID
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("❌ BOT_TOKEN is not set. Please add it in Render environment variables.")

# Flask app
app = Flask(__name__)

# Telegram bot application
application = Application.builder().token(TOKEN).build()

# === Handler to check who added the bot ===
async def check_who_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = update.my_chat_member
    # Check if bot was added to group
    if member.new_chat_member.status == "member" and member.new_chat_member.user.id == context.bot.id:
        chat_id = member.chat.id
        adder = member.from_user
        chat_title = member.chat.title if member.chat.title else "Private Chat"

        logger.info(f"✅ Bot added to group: {chat_title} (id={chat_id})")
        logger.info(f"👤 Added by: {adder.full_name} (id={adder.id}, username=@{adder.username})")

        if adder.id != BOT_OWNER_ID:
            logger.warning("❌ Not owner! Leaving group.")
            await context.bot.send_message(
                chat_id,
                "⚠️ Only my owner can add me to groups. Leaving..."
            )
            await context.bot.leave_chat(chat_id)
        else:
            await context.bot.send_message(
                chat_id,
                "✅ Bot added by my owner. Ready to work here!"
            )

# Register handler
application.add_handler(ChatMemberHandler(check_who_added, ChatMemberHandler.MY_CHAT_MEMBER))

# === Webhook route for Telegram ===
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

# Health check
@app.route("/")
def home():
    return "Bot is running on Render!", 200
