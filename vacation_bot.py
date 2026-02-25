import os
import json
import asyncio
import threading
from datetime import datetime, timedelta

from flask import Flask
from telegram import Bot
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
YEAR = 2026

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

bot = Bot(token=TOKEN)


def get_start_date(date_range):
    if not date_range:
        return None
    start = date_range.split("-")[0]
    day, month = start.split(".")
    return datetime(YEAR, int(month), int(day)).date()


async def check_vacations():
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    rows = sheet.get_all_records()

    today = datetime.now().date()

    for row in rows:
        name = row["ФИО"]

        for col in ["отпуск 1 часть дата", "отпуск 2 часть дата"]:
            start_date = get_start_date(row.get(col))

            if start_date:
                notify_date = start_date - timedelta(days=5)

                if notify_date == today:
                    await bot.send_message(
                        chat_id=CHAT_ID,
                        text=f"📌 Через 5 дней отпуск:\n{name} — с {start_date.strftime('%d.%m')}"
                    )


async def scheduler():
    while True:
        await check_vacations()
        await asyncio.sleep(86400)  # проверка раз в сутки


def run_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(scheduler())


@app.route("/")
def home():
    return "Bot is running!"


if __name__ == "__main__":
    threading.Thread(target=run_async_loop).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)



