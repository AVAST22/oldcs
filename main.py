import time
import threading
import requests
import telebot

from http.server import BaseHTTPRequestHandler, HTTPServer


# =========================================================
# НАСТРОЙКИ
# =========================================================

# =========================================================
# 1. TELEGRAM BOT TOKEN
# =========================================================

TELEGRAM_TOKEN = "8246666424:AAEhc4k0HzzV_NepsQokVZ54bUp90n-mpk0"


# =========================================================
# 2. GAMEHOST API KEY
# =========================================================

GAMEHOST_API_KEY = "ae8afe39e1aff19813bb264d5b52affd"


# =========================================================
# 3. GAMEHOST SERVER ID
# =========================================================

SERVER_ID = "5785"


# =========================================================
# 4. CS 1.6 SERVER
# =========================================================

SERVER_IP = "91.211.118.90"
SERVER_PORT = "27016"


# =========================================================
# 5. КАРТИНКА
# =========================================================

SERVER_IMAGE_URL = (
    "https://i.postimg.cc/3wh9H2pK/"
    "Chat-GPT-Image-16-avg-2026-g-22-11-04.png"
)


# =========================================================
# 6. RENDER PORT
# =========================================================

# Render передаёт PORT автоматически.
# Если переменной нет — используется 10000.

import os

PORT = int(
    os.environ.get(
        "PORT",
        "10000"
    )
)


# =========================================================
# TELEGRAM BOT
# =========================================================

bot = telebot.TeleBot(
    TELEGRAM_TOKEN
)


# =========================================================
# GAMEHOST API
# =========================================================

def get_server_status():

    url = "https://cp.gamehost.com.ua/api.html"

    params = {
        "action": "status",
        "id": SERVER_ID,
        "key": GAMEHOST_API_KEY
    }

    try:

        print(
            "[GAMEHOST] Запрос статуса сервера..."
        )

        response = requests.get(
            url,
            params=params,
            timeout=5
        )

        print(
            "[GAMEHOST] HTTP:",
            response.status_code
        )

        response.raise_for_status()

        data = response.json()

        print(
            "[GAMEHOST] JSON получен"
        )


        # =================================================
        # ПРОВЕРЯЕМ ONLINE
        # =================================================

        if not data.get(
            "online",
            False
        ):

            print(
                "[GAMEHOST] Сервер OFFLINE"
            )

            return None


        # =================================================
        # ДАННЫЕ СЕРВЕРА
        # =================================================

        info = data.get(
            "info",
            {}
        )


        game_map = info.get(
            "map",
            "Неизвестно"
        )


        players = info.get(
            "activeplayers",
            0
        )


        max_players = info.get(
            "maxplayers",
            32
        )


        # =================================================
        # ПРОВЕРЯЕМ ЧИСЛА
        # =================================================

        try:

            players = int(
                players
            )

        except (
            ValueError,
            TypeError
        ):

            players = 0


        try:

            max_players = int(
                max_players
            )

        except (
            ValueError,
            TypeError
        ):

            max_players = 32


        result = {

            "map": game_map,

            "players": players,

            "max_players": max_players

        }


        print(
            "[GAMEHOST] "
            f"Карта: {game_map} | "
            f"Игроки: "
            f"{players}/{max_players}"
        )


        return result


    except requests.exceptions.Timeout:

        print(
            "[GAMEHOST] "
            "ОШИБКА: timeout"
        )

        return None


    except requests.exceptions.ConnectionError as e:

        print(
            "[GAMEHOST] "
            f"ОШИБКА соединения: {e}"
        )

        return None


    except requests.exceptions.HTTPError as e:

        print(
            "[GAMEHOST] "
            f"HTTP ошибка: {e}"
        )

        return None


    except ValueError as e:

        print(
            "[GAMEHOST] "
            f"Ошибка JSON: {e}"
        )

        return None


    except Exception as e:

        print(
            "[GAMEHOST] "
            f"Неизвестная ошибка: {e}"
        )

        return None


# =========================================================
# TELEGRAM /info
# =========================================================

@bot.message_handler(
    commands=["info"]
)
def send_server_info(
    message
):

    print(
        "[TELEGRAM] Получена команда /info"
    )


    # =====================================================
    # GAMEHOST API
    # =====================================================

    info = get_server_status()


    # =====================================================
    # ТВОЙ ТЕКСТ
    # =====================================================

    if info:

        text = (
            "👑 <b>[OLD] SCHOOL ™</b>\n"
        )

        text += (
            f"🟢 <code>"
            f"{SERVER_IP}:{SERVER_PORT}"
            f"</code>\n"
        )

        text += (
            f"🗺 <b>Карта:</b> "
            f"{info['map']}\n"
        )

        text += (
            f"👥 <b>Игроки:</b> "
            f"{info['players']}/"
            f"{info['max_players']}\n"
        )

        text += (
            "🎮 <i>"
            "Заходи и покажи свой скилл!"
            "</i>"
        )


    else:

        text = (
            "👑 <b>[OLD] SCHOOL ™</b>\n"
        )

        text += (
            f"🔴 <code>"
            f"{SERVER_IP}:{SERVER_PORT}"
            f"</code>\n"
        )

        text += (
            "⚠️ <b>"
            "Сервер временно недоступен "
            "или выключен."
            "</b>"
        )


    # =====================================================
    # ОТПРАВЛЯЕМ КАРТИНКУ
    # =====================================================

    try:

        bot.send_photo(
            message.chat.id,
            SERVER_IMAGE_URL,
            caption=text,
            parse_mode="HTML",
            timeout=15
        )

        print(
            "[TELEGRAM] /info отправлен"
        )


    except Exception as e:

        print(
            "[TELEGRAM] "
            f"Ошибка отправки картинки: {e}"
        )


        # =================================================
        # ЕСЛИ КАРТИНКА НЕ ОТПРАВИЛАСЬ
        # =================================================

        try:

            bot.send_message(
                message.chat.id,
                text,
                parse_mode="HTML",
                timeout=15
            )

            print(
                "[TELEGRAM] "
                "Текстовый ответ отправлен"
            )


        except Exception as e2:

            print(
                "[TELEGRAM] "
                f"Ошибка отправки текста: {e2}"
            )


# =========================================================
# HTTP SERVER ДЛЯ RENDER
# =========================================================

class WebServer(
    BaseHTTPRequestHandler
):


    # =====================================================
    # GET
    # =====================================================

    def do_GET(
        self
    ):

        # -------------------------------------------------
        # Главная
        # -------------------------------------------------

        if self.path == "/":

            self.send_response(
                200
            )

            self.send_header(
                "Content-Type",
                "text/plain; charset=utf-8"
            )

            self.end_headers()

            self.wfile.write(
                b"OLDCS Telegram Bot is running!"
            )

            return


        # -------------------------------------------------
        # Health
        # -------------------------------------------------

        if self.path == "/health":

            self.send_response(
                200
            )

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.end_headers()

            self.wfile.write(
                b'{"status":"ok","bot":"running"}'
            )

            return


        # -------------------------------------------------
        # 404
        # -------------------------------------------------

        self.send_response(
            404
        )

        self.end_headers()


    # =====================================================
    # HEAD
    # =====================================================

    def do_HEAD(
        self
    ):

        self.send_response(
            200
        )

        self.end_headers()


    # =====================================================
    # LOG
    # =====================================================

    def log_message(
        self,
        format,
        *args
    ):

        print(
            "[HTTP]",
            format % args
        )


# =========================================================
# HTTP SERVER
# =========================================================

def run_web_server():

    server = HTTPServer(
        (
            "0.0.0.0",
            PORT
        ),
        WebServer
    )


    print(
        "[HTTP] Сервер запущен "
        f"на порту {PORT}"
    )


    server.serve_forever()


# =========================================================
# TELEGRAM POLLING
# =========================================================

def run_bot():

    print(
        "[BOT] Запускаю Telegram polling..."
    )


    while True:

        try:

            bot.infinity_polling(
                timeout=30,
                long_polling_timeout=30,
                skip_pending=True
            )


        except Exception as e:

            print(
                "[BOT] "
                f"Polling ошибка: {e}"
            )

            print(
                "[BOT] "
                "Перезапуск через 5 секунд..."
            )

            time.sleep(5)


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    print(
        "========================================"
    )

    print(
        "       OLDCS TELEGRAM BOT"
    )

    print(
        "========================================"
    )


    print(
        "[CONFIG] CS Server:",
        f"{SERVER_IP}:{SERVER_PORT}"
    )


    print(
        "[CONFIG] GameHost ID:",
        SERVER_ID
    )


    print(
        "[CONFIG] Render PORT:",
        PORT
    )


    # =====================================================
    # HTTP SERVER
    # =====================================================

    web_thread = threading.Thread(
        target=run_web_server,
        daemon=True
    )

    web_thread.start()


    # =====================================================
    # TELEGRAM BOT
    # =====================================================

    run_bot()
