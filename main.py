import os
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    ChatMemberHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =====================
# CONFIG
# =====================
BOT_TOKEN = "8466271055:AAEuITQNe4DXvSX2GFybR0oB-2cPmnc6Hs8"
BOT_OWNER_ID = 7124683213
PORT = int(os.environ.get("PORT", 5000))
WEBHOOK_URL = f"https://alstime-3.onrender.com/{BOT_TOKEN}"  # change if your render URL is different

# =====================
# FLASK APP
# =====================
app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()

# --- Case 1: When bot's membership changes (added/removed) ---
async def bot_status_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = update.my_chat_member
    if member.new_chat_member.status == "member" and member.new_chat_member.user.id == context.bot.id:
        chat_id = member.chat.id
        adder = member.from_user

        if adder.id != BOT_OWNER_ID:
            await context.bot.send_message(chat_id, "⚠️ Only my owner can add me. Leaving...")
            await context.bot.leave_chat(chat_id)
        else:
            await context.bot.send_message(chat_id, "✅ Added by my owner. Ready to work!")

# --- Case 2: When someone adds bot as "new_chat_member" ---
async def new_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        for user in update.message.new_chat_members:
            if user.id == context.bot.id:  # Bot was added
                chat_id = update.message.chat.id
                adder = update.message.from_user

                if adder.id != BOT_OWNER_ID:
                    await context.bot.send_message(chat_id, "⚠️ Only my owner can add me. Leaving...")
                    await context.bot.leave_chat(chat_id)
                else:
                    await context.bot.send_message(chat_id, "✅ Added by my owner. Ready to work!")

# Register handlers
application.add_handler(ChatMemberHandler(bot_status_update, ChatMemberHandler.MY_CHAT_MEMBER))
application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member_handler))

# =====================
# FLASK ROUTES
# =====================
@app.route("/")
def home():
    return "Bot is running on Render!"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

# =====================
# STARTUP
# =====================
if __name__ == "__main__":
    # Set webhook
    import requests
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}")
    print(f"Webhook set to {WEBHOOK_URL}")

    app.run(host="0.0.0.0", port=PORT)
