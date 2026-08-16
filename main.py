import telebot
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import re

TOKEN = "8246666424:AAEhc4k0HzzV_NepsQokVZ54bUp90n-mpk0"
bot = telebot.TeleBot(TOKEN)

# Данные вашего сервера CS 1.6
SERVER_IP = "91.211.118.90"
SERVER_PORT = "27016"

# Рабочая картинка-заглушка (можете заменить на свою прямую ссылку)
SERVER_IMAGE_URL = "https://i.postimg.cc/3wh9H2pK/Chat-GPT-Image-16-avg-2026-g-22-11-04.png"

def get_server_status(ip, port):
    try:
        # Запрос к официальному публичному мониторингу GameHost для вашего сервера (ID: 5785)
        url = "https://gamehost.com.ua"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=3.0)
        
        if response.status_code == 200:
            html_text = response.text
            
            # Извлекаем карту и игроков прямо со страницы хостинга
            map_search = re.search(r'Карта:.*?<b>(.*?)</b>', html_text, re.IGNORECASE)
            players_search = re.search(r'Игроки:.*?<b>(\d+)/(\d+)</b>', html_text, re.IGNORECASE)
            
            return {
                "map": map_search.group(1).strip() if map_search else "Неизвестно",
                "players": int(players_search.group(1)) if players_search else 0,
                "max_players": int(players_search.group(2)) if players_search else 32
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
        bot.send_photo(message.chat.id, SERVER_IMAGE_URL, caption=text, parse_mode="HTML")
    except Exception:
        bot.send_message(message.chat.id, text, parse_mode="HTML")

class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

    def do_HEAD(self):
        # Исправление для Render: теперь хостинг сможет проверять статус бота без ошибок
        self.send_response(200)
        self.end_headers()

def run_web_server():
    server = HTTPServer(('0.0.0.0', 10000), WebServer)
    server.serve_forever()

if __name__ == '__main__':
    threading.Thread(target=run_web_server, daemon=True).start()
    print("Бот успешно запущен...")
    bot.infinity_polling()

