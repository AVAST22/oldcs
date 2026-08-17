import os
import time
import threading
import requests
import telebot

from http.server import BaseHTTPRequestHandler, HTTPServer


# =========================================================
# НАСТРОЙКИ
# =========================================================

# Telegram Bot Token берём из Render Environment
TOKEN = os.environ.get("8246666424:AAEhc4k0HzzV_NepsQokVZ54bUp90n-mpk0")

if not TOKEN:
    raise RuntimeError(
        "ОШИБКА: не задан BOT_TOKEN в Environment Variables"
    )

bot = telebot.TeleBot(TOKEN)


# =========================================================
# CS 1.6 СЕРВЕР
# =========================================================

SERVER_IP = "91.211.118.90"
SERVER_PORT = "27016"

# ID сервера GameHost
SERVER_ID = "5785"

# API ключ GameHost берём из Render Environment
GAMEHOST_API_KEY = os.environ.get("ae8afe39e1aff19813bb264d5b52affd")

if not GAMEHOST_API_KEY:
    raise RuntimeError(
        "ОШИБКА: не задан GAMEHOST_API_KEY "
        "в Environment Variables"
    )


# =========================================================
# КАРТИНКА
# =========================================================

SERVER_IMAGE_URL = (
    "https://i.postimg.cc/3wh9H2pK/"
    "Chat-GPT-Image-16-avg-2026-g-22-11-04.png"
)


# =========================================================
# RENDER
# =========================================================

# Render автоматически предоставляет эту переменную
RENDER_URL = os.environ.get(
    "RENDER_EXTERNAL_URL",
    ""
).rstrip("/")


# Render автоматически предоставляет PORT
PORT = int(
    os.environ.get(
        "PORT",
        "10000"
    )
)


# Секрет Telegram Webhook
WEBHOOK_SECRET = os.environ.get(
    "WEBHOOK_SECRET",
    "oldcsinua_webhook_2026"
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
            "[GAMEHOST API] Запрашиваем статус "
            f"сервера ID={SERVER_ID}"
        )

        response = requests.get(
            url,
            params=params,
            timeout=(3, 5)
        )

        print(
            "[GAMEHOST API] HTTP status:",
            response.status_code
        )

        response.raise_for_status()

        data = response.json()

        print(
            "[GAMEHOST API] JSON получен"
        )

        # -------------------------------------------------
        # Проверяем online
        # -------------------------------------------------

        if not data.get("online", False):

            print(
                "[GAMEHOST API] Сервер OFFLINE"
            )

            return None


        # -------------------------------------------------
        # Получаем info
        # -------------------------------------------------

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


        # -------------------------------------------------
        # Приводим значения к числам
        # -------------------------------------------------

        try:
            players = int(players)
        except (ValueError, TypeError):
            players = 0

        try:
            max_players = int(max_players)
        except (ValueError, TypeError):
            max_players = 32


        result = {
            "map": game_map,
            "players": players,
            "max_players": max_players
        }


        print(
            "[GAMEHOST API] "
            f"Карта={game_map}, "
            f"Игроки={players}/{max_players}"
        )

        return result


    except requests.exceptions.Timeout:

        print(
            "[GAMEHOST API] ОШИБКА: timeout"
        )

        return None


    except requests.exceptions.ConnectionError as e:

        print(
            "[GAMEHOST API] "
            f"ОШИБКА соединения: {e}"
        )

        return None


    except requests.exceptions.HTTPError as e:

        print(
            "[GAMEHOST API] "
            f"HTTP ошибка: {e}"
        )

        return None


    except requests.exceptions.RequestException as e:

        print(
            "[GAMEHOST API] "
            f"Ошибка запроса: {e}"
        )

        return None


    except ValueError as e:

        print(
            "[GAMEHOST API] "
            f"Ошибка JSON: {e}"
        )

        return None


    except Exception as e:

        print(
            "[GAMEHOST API] "
            f"Неизвестная ошибка: {e}"
        )

        return None


# =========================================================
# TELEGRAM /info
# =========================================================

@bot.message_handler(
    commands=["info"]
)
def send_server_info(message):

    print(
        "[TELEGRAM] Получена команда /info "
        f"от {message.from_user.id}"
    )


    # -----------------------------------------------------
    # Получаем информацию через GameHost API
    # -----------------------------------------------------

    info = get_server_status()


    # -----------------------------------------------------
    # ТЕКСТ НЕ МЕНЯЕМ
    # -----------------------------------------------------

    if info:

        text = f"👑 <b>[OLD] SCHOOL ™</b>\n"
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
            f"🎮 <i>"
            f"Заходи и покажи свой скилл!"
            f"</i>"
        )

    else:

        text = f"👑 <b>[OLD] SCHOOL ™</b>\n"
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


    # -----------------------------------------------------
    # Отправляем картинку
    # -----------------------------------------------------

    try:

        bot.send_photo(
            message.chat.id,
            SERVER_IMAGE_URL,
            caption=text,
            parse_mode="HTML",
            timeout=15
        )

        print(
            "[TELEGRAM] /info успешно отправлен"
        )


    except Exception as e:

        print(
            "[TELEGRAM] Ошибка отправки "
            f"картинки: {e}"
        )


        # -------------------------------------------------
        # Если картинка не отправилась —
        # отправляем обычный текст
        # -------------------------------------------------

        try:

            bot.send_message(
                message.chat.id,
                text,
                parse_mode="HTML",
                timeout=15
            )

            print(
                "[TELEGRAM] Текстовый ответ отправлен"
            )

        except Exception as e2:

            print(
                "[TELEGRAM] Ошибка отправки "
                f"текста: {e2}"
            )


# =========================================================
# WEB SERVER
# =========================================================

class WebServer(
    BaseHTTPRequestHandler
):


    # -----------------------------------------------------
    # Отключаем стандартный шум HTTP-сервера
    # -----------------------------------------------------

    def log_message(
        self,
        format,
        *args
    ):

        print(
            "[HTTP]",
            format % args
        )


    # =====================================================
    # GET
    # =====================================================

    def do_GET(self):


        # -------------------------------------------------
        # Главная страница
        # -------------------------------------------------

        if self.path == "/":

            self.send_response(200)

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
        # Health check
        # -------------------------------------------------

        if self.path == "/health":

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8"
            )

            self.end_headers()

            self.wfile.write(
                b'{"status":"ok","bot":"running"}'
            )

            return


        # -------------------------------------------------
        # Неизвестный адрес
        # -------------------------------------------------

        self.send_response(404)

        self.end_headers()


    # =====================================================
    # HEAD
    # =====================================================

    def do_HEAD(self):

        self.send_response(200)

        self.end_headers()


    # =====================================================
    # POST — TELEGRAM WEBHOOK
    # =====================================================

    def do_POST(self):


        # -------------------------------------------------
        # Проверяем URL webhook
        # -------------------------------------------------

        if not self.path.startswith(
            "/telegram-webhook"
        ):

            self.send_response(404)

            self.end_headers()

            return


        # -------------------------------------------------
        # Проверяем секрет Telegram
        # -------------------------------------------------

        received_secret = self.headers.get(
            "X-Telegram-Bot-Api-Secret-Token"
        )


        if received_secret != WEBHOOK_SECRET:

            print(
                "[SECURITY] "
                "Неверный webhook secret"
            )

            self.send_response(403)

            self.end_headers()

            return


        try:

            # -------------------------------------------------
            # Читаем тело запроса
            # -------------------------------------------------

            content_length = int(
                self.headers.get(
                    "Content-Length",
                    "0"
                )
            )


            body = self.rfile.read(
                content_length
            )


            # -------------------------------------------------
            # JSON от Telegram
            # -------------------------------------------------

            json_string = body.decode(
                "utf-8"
            )


            update = (
                telebot.types.Update
                .de_json(json_string)
            )


            print(
                "[WEBHOOK] Получен update:",
                update.update_id
            )


            # -------------------------------------------------
            # Обрабатываем update отдельно
            # -------------------------------------------------

            threading.Thread(
                target=process_update,
                args=(update,),
                daemon=True
            ).start()


            # -------------------------------------------------
            # Быстро отвечаем Telegram
            # -------------------------------------------------

            self.send_response(200)

            self.end_headers()

            self.wfile.write(
                b"OK"
            )


        except Exception as e:

            print(
                "[WEBHOOK] Ошибка:",
                e
            )


            # Telegram получит 200,
            # чтобы не повторять update бесконечно

            self.send_response(200)

            self.end_headers()

            self.wfile.write(
                b"OK"
            )


# =========================================================
# ОБРАБОТКА TELEGRAM UPDATE
# =========================================================

def process_update(update):

    try:

        bot.process_new_updates(
            [update]
        )

        print(
            "[WEBHOOK] Update обработан:",
            update.update_id
        )

    except Exception as e:

        print(
            "[WEBHOOK] Ошибка обработки:",
            e
        )


# =========================================================
# ЗАПУСК HTTP СЕРВЕРА
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
        "[HTTP] Web server запущен "
        f"на порту {PORT}"
    )


    server.serve_forever()


# =========================================================
# TELEGRAM WEBHOOK
# =========================================================

def setup_webhook():


    # -----------------------------------------------------
    # Проверяем URL Render
    # -----------------------------------------------------

    if not RENDER_URL:

        print(
            "[WEBHOOK] ОШИБКА: "
            "RENDER_EXTERNAL_URL отсутствует"
        )

        return


    webhook_url = (
        f"{RENDER_URL}"
        f"/telegram-webhook"
    )


    try:

        # -------------------------------------------------
        # Удаляем старый webhook
        # -------------------------------------------------

        bot.remove_webhook()

        print(
            "[WEBHOOK] Старый webhook удалён"
        )


        # -------------------------------------------------
        # Устанавливаем новый
        # -------------------------------------------------

        result = bot.set_webhook(
            url=webhook_url,
            secret_token=WEBHOOK_SECRET,
            drop_pending_updates=True
        )


        print(
            "[WEBHOOK] Установлен:",
            result
        )


        print(
            "[WEBHOOK] URL:",
            webhook_url
        )


    except Exception as e:

        print(
            "[WEBHOOK] Ошибка установки:",
            e
        )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    print(
        "======================================"
    )

    print(
        "      OLDCS TELEGRAM BOT"
    )

    print(
        "======================================"
    )


    print(
        "[CONFIG] Server:",
        f"{SERVER_IP}:{SERVER_PORT}"
    )


    print(
        "[CONFIG] GameHost ID:",
        SERVER_ID
    )


    print(
        "[CONFIG] Render URL:",
        RENDER_URL or "НЕ НАЙДЕН"
    )


    print(
        "[CONFIG] Port:",
        PORT
    )


    # -----------------------------------------------------
    # Запускаем HTTP
    # -----------------------------------------------------

    web_thread = threading.Thread(
        target=run_web_server,
        daemon=True
    )

    web_thread.start()


    # -----------------------------------------------------
    # Даём HTTP серверу запуститься
    # -----------------------------------------------------

    time.sleep(1)


    # -----------------------------------------------------
    # Устанавливаем Telegram webhook
    # -----------------------------------------------------

    setup_webhook()


    print(
        "======================================"
    )

    print(
        "[BOT] Бот успешно запущен!"
    )

    print(
        "[BOT] Webhook активен."
    )

    print(
        "======================================"
    )


    # -----------------------------------------------------
    # Держим основной процесс живым
    # -----------------------------------------------------

    try:

        while True:

            time.sleep(60)

    except KeyboardInterrupt:

        print(
            "[BOT] Остановка..."
        )

        try:

            bot.remove_webhook()

        except Exception:

            pass
