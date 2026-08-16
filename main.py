import telebot
import socket
import struct
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

TOKEN = "8246666424:AAEhc4k0HzzV_NepsQokVZ54bUp90n-mpk0"
bot = telebot.TeleBot(TOKEN)

# Ваш актуальный IP и ПОРТ сервера CS 1.6
SERVER_IP = "91.211.118.90"
SERVER_PORT = 27016

def query_gold_source(ip, port):
    addr = (ip, port)
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

    try:
        payload = data[5:]
        protocol = payload
        payload = payload[1:]
        
        server_name, payload = payload.split(b'\x00', 1)
        map_name, payload = payload.split(b'\x00', 1)
        folder, payload = payload.split(b'\x00', 1)
        game, payload = payload.split(b'\x00', 1)
        
        app_id = struct.unpack('<H', payload[:2])
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
        # Красивое и стильное оформление, которое вы просили
        text = f"👑 <b>[OLD] SCHOOL ™</b>\n"
        text += f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        text += f"🟢 <code>{SERVER_IP}:{SERVER_PORT}</code>\n"
        text += f"🗺 <b>Карта:</b> {info['map']}\n"
        text += f"👥 <b>Гравців:</b> {info['players']}/{info['max_players']}\n"
        text += f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        text += f"🎮 <i>Заходь та покажи свой скілл!</i>"
    else:
        text = f"👑 <b>[OLD] SCHOOL ™</b>\n"
        text += f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        text += f"🟡 <code>{SERVER_IP}:{SERVER_PORT}</code>\n\n"
        text += "❌ <b>Сервер тимчасово недоступний або вимкнений.</b>"

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
