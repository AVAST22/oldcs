import os
import threading
import requests
import telebot

from http.server import BaseHTTPRequestHandler, HTTPServer


# ==============================
# НАСТРОЙКИ
# ==============================

TOKEN = "8246666424:AAEhc4k0HzzV_NepsQokVZ54bUp90n-mpk0"
GAMEHOST_API_KEY = "ae8afe39e1aff19813bb264d5b52affd"

SERVER_ID = "5785"

SERVER_IP = "91.211.118.111"
SERVER_PORT = "27015"

SERVER_IMAGE_URL = "https://i.postimg.cc/3wh9H2pK/Chat-GPT-Image-16-avg-2026-g-22-11-04.png"


bot = telebot.TeleBot(TOKEN)


# ==============================
# GAMEHOST API
# ==============================

def get_server_status():

    try:

        response = requests.get(
            "https://cp.gamehost.com.ua/api.html",
            params={
                "action": "status",
                "id": SERVER_ID,
                "key": GAMEHOST_API_KEY
            },
            timeout=5
        )

        data = response.json()

        if data.get("online"):

            info = data["info"]

            return (
                info.get("map", "Неизвестно"),
                info.get("activeplayers", 0),
                info.get("maxplayers", 32)
            )

    except Exception:
        pass

    return None


# ==============================
# /info
# ==============================

@bot.message_handler(commands=["info"])
def info(message):

    server = get_server_status()

    if server:

        game_map, players, max_players = server

        text = (
            "👑 <b>[OLD] SCHOOL ™</b>\n"
            f"🟢 <code>{SERVER_IP}:{SERVER_PORT}</code>\n"
            f"🗺 <b>Карта:</b> {game_map}\n"
            f"👥 <b>Игроки:</b> {players}/{max_players}\n"
            "🎮 <i>Заходи и покажи свой скилл!</i>"
        )

    else:

        text = (
            "👑 <b>[OLD] SCHOOL ™</b>\n"
            f"🔴 <code>{SERVER_IP}:{SERVER_PORT}</code>\n"
            "⚠️ <b>Сервер временно недоступен или выключен.</b>"
        )

    try:

        bot.send_photo(
            message.chat.id,
            SERVER_IMAGE_URL,
            caption=text,
            parse_mode="HTML"
        )

    except Exception:

        bot.send_message(
            message.chat.id,
            text,
            parse_mode="HTML"
        )


# ==============================
# RENDER
# ==============================

class WebServer(BaseHTTPRequestHandler):

    def do_GET(self):

        self.send_response(200)
        self.end_headers()

        self.wfile.write(
            b"OLDCS Bot is running!"
        )


def run_web():

    port = int(
        os.environ.get("PORT", 10000)
    )

    server = HTTPServer(
        ("0.0.0.0", port),
        WebServer
    )

    server.serve_forever()


# ==============================
# START
# ==============================

if __name__ == "__main__":

    threading.Thread(
        target=run_web,
        daemon=True
    ).start()

    bot.infinity_polling(
        timeout=30,
        long_polling_timeout=30
    )
