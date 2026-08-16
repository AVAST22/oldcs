import telebot
import socket
import struct
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

TOKEN = "8246666424:AAEhc4k0HzzV_NepsQokVZ54bUp90n-mpk0"
bot = telebot.TeleBot(TOKEN)

SERVER_IP = "91.211.118.111"
SERVER_PORT = 27015

def query_gold_source(ip, port):
    addr = (ip, port)
    
    # Запрос A2S_INFO
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2.5)
    try:
        sock.sendto(b'\xFF\xFF\xFF\xFFTSource Engine Query\x00', addr)
        data, _ = sock.recvfrom(4096)
    except socket.timeout:
        return None
    finally:
        sock.close()

    if not data.startswith(b'\xFF\xFF\xFF\xFFI'):
        return None

    # Парсинг A2S_INFO ответа
    try:
        payload = data[5:]
        protocol = payload[0]
        payload = payload[1:]
        
        # Чтение строк (название сервера, карта, папка, игра)
        server_name, payload = payload.split(b'\x00', 1)
        map_name, payload = payload.split(b'\x00', 1)
        folder, payload = payload.split(b'\x00', 1)
        game, payload = payload.split(b'\x00', 1)
        
        # Чтение числовых данных
        app_id = struct.unpack('<H', payload[:2])[0]
        players = payload[2]
        max_players = payload[3]
        
        return {
            "map": map_name.decode('utf-8', errors='ignore'),
            "players": players,
            "max_players": max_players
        }
    except Exception:
        return None

@bot.message_handler(commands=['info'])
def send_server_info(message):
    info = query_gold_source(SERVER_IP, SERVER_PORT)
    
    if info:
        text = f"🎮 [OLD] SCHOOL ™\n"
        text += f"🌍 IP: {SERVER_IP}:{SERVER_PORT}\n"
        text += f"🗺 Карта: {info['map']}\n\n"
        text += f"Игроки: {info['players']}/{info['max_players']}\n"
        text += "📝 Для просмотра ников зайдите на сервер!"
    else:
        text = f"🎮 [OLD] SCHOOL ™\n"
        text += f"🌍 IP: {SERVER_IP}:{SERVER_PORT}\n\n"
        text += "❌ Сервер временно недоступен или выключен."

    bot.reply_to(message, text)

# Веб-сервер заглушка для Render
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
