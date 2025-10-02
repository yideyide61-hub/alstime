import os
import logging
from flask import Flask
from telegram import Update
from telegram.ext import Application, ChatMemberHandler, ContextTypes

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_OWNER_ID = 7124683213  # replace with your Telegram ID

# Load token from Render environment variable
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("❌ BOT_TOKEN is not set. Please add it in Render environment variables.")

# Flask app (needed for Render)
app = Flask(__name__)

# Telegram bot application
application = Application.builder().token(TOKEN).build()

# === Handler to check who added the bot ===
async def check_who_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = update.my_chat_member
    if member.new_chat_member.user.id == context.bot.id:
        chat_id = member.chat.id
        adder = member.from_user
        chat_title = member.chat.title if member.chat.title else "Private Chat"

        logger.info(f"✅ Bot added to group: {chat_title} (id={chat_id})")
        logger.info(f"👤 Added by: {adder.full_name} (id={adder.id}, username=@{adder.username})")

        # Restrict who can add the bot
        if adder.id != BOT_OWNER_ID:
            await context.bot.leave_chat(chat_id)

# Register handler
application.add_handler(ChatMemberHandler(check_who_added, ChatMemberHandler.MY_CHAT_MEMBER))

# Flask route (for health check in Render)
@app.route("/")
def home():
    return "Bot is running on Render!", 200

# Start polling when running locally
if __name__ == "__main__":
    import asyncio
    asyncio.run(application.run_polling())

