import telebot
from opengsq import Goldsource
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Токен вашего бота из BotFather
TOKEN = "8246666424:AAEhc4k0HzzV_NepsQokVZ54bUp90n-mpk0"
bot = telebot.TeleBot(TOKEN)

# IP-адрес вашего сервера CS 1.6
SERVER_IP = "91.211.118.111"
SERVER_PORT = 27015

@bot.message_handler(commands=['info'])
def send_server_info(message):
    try:
        # Подключаемся к серверу CS 1.6
        gs = Goldsource(SERVER_IP, SERVER_PORT, timeout=3.0)
        info = gs.get_info()
        players_data = gs.get_players()

        # Формируем список игроков
        player_list = []
        if players_data:
            for p in players_data:
                name = p.get('name', '').strip()
                if name:  # Игнорируем пустые имена
                    player_list.append(f"• {name}")

        # Собираем красивый текст сообщения
        text = f"🎮 [OLD] SCHOOL ™\n"
        text += f"🌍 IP: {SERVER_IP}:{SERVER_PORT}\n"
        text += f"🗺 Карта: {info.get('map', 'Неизвестно')}\n\n"
        text += f"Игроки: {info.get('players', 0)}/{info.get('max_players', 32)}\n"

        if player_list:
            text += "\n".join(player_list)
        else:
            text += "🚫 Игроки отсутствуют"

    except Exception as e:
        # Если сервер выключен или недоступен
        text = f"🎮 [OLD] SCHOOL ™\n"
        text += f"🌍 IP: {SERVER_IP}:{SERVER_PORT}\n\n"
        text += "❌ Сервер временно недоступен или выключен."

    # Отправляем ответ в группу
    bot.reply_to(message, text)

# Заглушка-сервер, чтобы Render считал приложение активным
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

    threading.Thread(target=run_web_server, daemon=True).start()
    bot.infinity_polling()
