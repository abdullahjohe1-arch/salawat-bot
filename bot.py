import os
import re
import requests
from flask import Flask, request

TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

API = f"https://api.telegram.org/bot{TOKEN}"
app = Flask(__name__)


def telegram(method, data):
    return requests.post(
        f"{API}/{method}",
        json=data,
        timeout=20
    ).json()


@app.route("/", methods=["GET"])
def home():
    return "Salawat Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(silent=True) or {}

    callback = update.get("callback_query")

    if callback:
        callback_id = callback["id"]
        message = callback.get("message")

        # تأكيد الضغطة
        telegram("answerCallbackQuery", {
            "callback_query_id": callback_id
        })

        if message:
            chat_id = message["chat"]["id"]
            message_id = message["message_id"]
            text = message.get("text", "")

            # قراءة الرقم الحالي من زر القلب
            match = re.search(r"❤️.*?(\d+)", text)

            if match:
                old_count = int(match.group(1))
            else:
                old_count = 0

            new_count = old_count + 1

            # تحديث الرقم داخل النص
            if match:
                new_text = re.sub(
                    r"(❤️.*?)(\d+)",
                    rf"\g<1>{new_count}",
                    text,
                    count=1
                )
            else:
                new_text = text + f"\n\n❤️ {new_count}"

            telegram("editMessageText", {
                "chat_id": chat_id,
                "message_id": message_id,
                "text": new_text,
                "reply_markup": {
                    "inline_keyboard": [
                        [
                            {
                                "text": f"❤️ {new_count}",
                                "callback_data": "salawat"
                            }
                        ]
                    ]
                }
            })

    return "OK"


@app.route("/create", methods=["GET"])
def create_post():
    text = "اللهم صلِّ على محمد وآل محمد ﷺ\n\n❤️ 0"

    result = telegram("sendMessage", {
        "chat_id": CHANNEL_ID,
        "text": text,
        "reply_markup": {
            "inline_keyboard": [
                [
                    {
                        "text": "❤️ 0",
                        "callback_data": "salawat"
                    }
                ]
            ]
        }
    })

    return str(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
