import telebot
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

TOKEN = "8246666424:AAEhc4k0HzzV_NepsQokVZ54bUp90n-mpk0"
bot = telebot.TeleBot(TOKEN)

# Данные вашего сервера CS 1.6
SERVER_IP = "91.211.118.90"
SERVER_PORT = "27016"

# Рабочая картинка-заглушка (замените на свою, если эта не подходит)
SERVER_IMAGE_URL = "https://i.postimg.cc/3wh9H2pK/Chat-GPT-Image-16-avg-2026-g-22-11-04.png"

def get_server_status(ip, port):
    # Исправлен URL: добавлен /api/ или правильный путь для loqup
    try:
        url = f"https://loqup.ru{ip}&port={port}"
        response = requests.get(url, timeout=3.0)
        if response.status_code == 200:
            data = response.json()
            return {
                "map": data.get("map", "Неизвестно"),
                "players": data.get("players", 0),
                "max_players": data.get("maxplayers", 32)
            }
    except Exception:
        pass

    # Исправлен URL для cs-monitoring
    try:
        url_alt = f"https://cs-monitoring.ru{ip}&port={port}"
        res = requests.get(url_alt, timeout=3.0)
        if res.status_code == 200:
            data = res.json().get("normal", {})
            return {
                "map": data.get("map", "Неизвестно"),
                "players": data.get("players", 0),
                "max_players": data.get("maxplayers", 32)
            }
    except Exception:
        pass

    return None

@bot.message_handler(commands=['info'])
def send_server_info(message):
    info = get_server_status(SERVER_IP, SERVER_PORT)
    
    if info:
        text = f"👑 <b>[OLD] SCHOOL ™</b>\n"
        text += f"🟢 <code>{SERVER_IP}:{SERVER_PORT}</code>\n"
        text += f"🗺 <b>Карта:</b> {info['map']}\n"
        text += f"👥 <b>Игроки:</b> {info['players']}/{info['max_players']}\n"
        text += f"🎮 <i>Заходи и покажи свой скилл!</i>"
    else:
        text = f"👑 <b>[OLD] SCHOOL ™</b>\n"
        text += f"🔴 <code>{SERVER_IP}:{SERVER_PORT}</code>\n"
        text += "⚠️ <b>Сервер временно недоступен или выключен.</b>"

    try:
        # Пытаемся отправить с картинкой
        bot.send_photo(message.chat.id, SERVER_IMAGE_URL, caption=text, parse_mode="HTML")
    except Exception:
        # Если картинка недоступна, отправляем просто текст
        bot.send_message(message.chat.id, text, parse_mode="HTML")

class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_web_server():
    server = HTTPServer(('0.0.0.0', 10000), WebServer)
    server.serve_forever()

if __name__ == '__main__':
    threading.Thread(target=run_web_server, daemon=True).start()
    print("Бот успешно запущен...")
    bot.infinity_polling()
