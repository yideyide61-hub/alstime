import os
import logging
from flask import Flask, request
from telegram import Update, ChatMember
from telegram.ext import Application, ChatMemberHandler, ContextTypes

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_OWNER_ID = 7124683213  # replace with your Telegram ID
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("❌ BOT_TOKEN is not set. Please add it in Render environment variables.")

# Flask app (needed for Render)
app = Flask(__name__)

# Telegram bot application
application = Application.builder().token(TOKEN).build()


# === Handler: check who added the bot ===
async def check_who_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member: ChatMember = update.my_chat_member
    if member.new_chat_member.user.id == context.bot.id:  # bot was added
        chat_id = member.chat.id
        adder = member.from_user
        chat_title = member.chat.title if member.chat.title else "Private Chat"

        logger.info(f"✅ Bot added to group: {chat_title} (id={chat_id})")
        logger.info(f"👤 Added by: {adder.full_name} (id={adder.id}, username=@{adder.username})")

        try:
            # Get adder's status in the group (creator, admin, member, etc.)
            adder_status = (await context.bot.get_chat_member(chat_id, adder.id)).status
        except Exception as e:
            logger.error(f"⚠️ Could not fetch adder's status: {e}")
            adder_status = None

        # Only allow if group owner/creator, administrator, or BOT_OWNER_ID
        if adder.id == BOT_OWNER_ID or adder_status in ["creator", "administrator"]:
            logger.info("✅ Allowed: Bot stays in the group.")
        else:
            logger.warning("⛔ Not allowed: Leaving the group.")
            await context.bot.leave_chat(chat_id)


# Register handler
application.add_handler(ChatMemberHandler(check_who_added, ChatMemberHandler.MY_CHAT_MEMBER))


# Flask route (health check)
@app.route("/")
def home():
    return "Bot is running on Render!", 200


# Webhook route (for Render deployment)
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    from flask import request
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200


# Local testing (polling)
if __name__ == "__main__":
    import asyncio
    asyncio.run(application.run_polling())

