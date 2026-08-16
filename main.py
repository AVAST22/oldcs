import telebot
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

TOKEN = "8246666424:AAEhc4k0HzzV_NepsQokVZ54bUp90n-mpk0"
bot = telebot.TeleBot(TOKEN)

# Данные вашего сервера CS 1.6
SERVER_IP = "91.211.118.90"
SERVER_PORT = "27016"

# Ссылка на картинку сервера. Вы можете заменить её на свою (ссылка должна заканчиваться на .jpg или .png)
SERVER_IMAGE_URL = "https://cdn.phototourl.com/free/2026-08-16-bfb49bdc-a40b-4735-93e2-61ea5a6c413f.jpg"

def get_server_status(ip, port):
    try:
        url = f"https://loqup.ru{ip}:{port}"
        response = requests.get(url, timeout=1.5)
        if response.status_code == 200:
            data = response.json()
            return {
                "map": data.get("map", "Неизвестно"),
                "players": data.get("players", 0),
                "max_players": data.get("maxplayers", 32)
            }
    except Exception:
        pass
    
    try:
        url_alt = f"https://cs-monitoring.ru{ip}&port={port}"
        res = requests.get(url_alt, timeout=1.5)
        if res.status_code == 200:
            data = res.json().get("normal", {})
            return {
                "map": data.get("map", "Неизвестно"),
                "players": data.get("players", 0),
                "max_players": data.get("maxplayers", 32)
            }
    except Exception:
        pass

    try:
        url_third = f"https://gs4u.net{ip}:{port}"
        res = requests.get(url_third, timeout=1.5)
        if res.status_code == 200:
            data = res.json()
            return {
                "map": data.get("map", "Неизвестно"),
                "players": data.get("players", 0),
                "max_players": data.get("maxplayers", 32)
            }
    except Exception:
        return None

@bot.message_handler(commands=['info'])
def send_server_info(message):
    info = get_server_status(SERVER_IP, SERVER_PORT)
    
    if info:
        # Текст, который пойдет под картинку (когда сервер работает)
        text = f"👑 <b>[OLD] SCHOOL ™</b>\n"
        text += f"🟢 <code>{SERVER_IP}:{SERVER_PORT}</code>\n"
        text += f"🗺 <b>Карта:</b> {info['map']}\n"
        text += f"👥 <b>Игроки:</b> {info['players']}/{info['max_players']}\n"
        text += f"🎮 <i>Заходи и покажи свой скилл!</i>"
    else:
        # Текст, который пойдет под картинку (когда сервер отключен)
        text = f"👑 <b>[OLD] SCHOOL ™</b>\n"
        text += f"🔴 <code>{SERVER_IP}:{SERVER_PORT}</code>\n"
        text += "⚠️ <b>Сервер временно недоступен или выключен.</b>"

    try:
        # Бот отправляет картинку, а текст прикрепляет снизу как подпись (caption)
        bot.send_photo(message.chat.id, SERVER_IMAGE_URL, caption=text, parse_mode="HTML")
    except Exception:
        # Если с картинкой что-то не так, бот отправит просто текстовое сообщение, чтобы не зависнуть
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
    bot.infinity_polling()
