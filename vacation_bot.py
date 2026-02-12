import os
import json
import asyncio
from datetime import datetime, timedelta

import gspread
from google.oauth2.service_account import Credentials
from telegram import Bot


# ==== НАСТРОЙКИ ====
TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = int(os.environ["CHAT_ID"])
YEAR = 2026

SPREADSHEET_ID = "1h8ftaZETqUBfVfRUyl_EGpiMQfyS32HmyG0ysgNKDaY"

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


# ==== ОСНОВНАЯ ПРОВЕРКА ====
async def check_vacations():
    bot = Bot(token=TOKEN)

    creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)

    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    rows = sheet.get_all_records()

    today = datetime.now().date()

    def get_start_date(date_range):
        if not date_range:
            return None
        try:
            start = str(date_range).split("-")[0]
            day, month = start.strip().split(".")
            return datetime(YEAR, int(month), int(day)).date()
        except:
            return None

    for row in rows:
        name = row.get("ФИО")

        for col in ["отпуск 1 часть дата", "отпуск 2 часть дата"]:
            start_date = get_start_date(row.get(col))

            if start_date:
                notify_date = start_date - timedelta(days=5)

                if notify_date == today:
                    await bot.send_message(
                        chat_id=CHAT_ID,
                        text=f"📌 Через 5 дней отпуск:\n{name} — с {start_date.strftime('%d.%m')}"
                    )


# ==== ПЛАНИРОВЩИК 24/7 ====
async def scheduler():
    while True:
        now = datetime.now()

        # Проверка каждый день в 09:00
        if now.hour == 16 and now.minute == 30:
            print("Проверка отпусков...")
            await check_vacations()
            await asyncio.sleep(60)  # чтобы не сработало 2 раза

        await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(scheduler())
