
# import os
# import sqlite3
# from datetime import datetime
# import pandas as pd
# import pytz
# import asyncio
# import nest_asyncio
# import requests
# from flask import Flask, render_template, request, redirect, url_for, send_file
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import (
#     Application,
#     CommandHandler,
#     CallbackContext,
#     CallbackQueryHandler,
# )

# app = Flask(__name__)
# DB_PATH = 'crm.db'
# BOT_TOKEN = '7935396412:AAHJS61QJTdHtaf7pNrwtEqNdxZrWgapOR4'
# ADMIN_CHAT_IDS = [6855997739, 266123144, 1657599027, 6449680789]


# def init_db():
#     if not os.path.exists(DB_PATH):
#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute('''
#             CREATE TABLE tolovlar (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 ismi TEXT NOT NULL,
#                 tolov INTEGER NOT NULL,
#                 kurs TEXT NOT NULL,
#                 oy TEXT NOT NULL,
#                 izoh TEXT,
#                 admin TEXT NOT NULL,
#                 oqituvchi TEXT NOT NULL,
#                 vaqt TEXT NOT NULL,
#                 tolov_turi TEXT
#             )
#         ''')
#         con.commit()
#         con.close()


# init_db()


# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         ismi = request.form['ismi']
#         tolov = int(request.form['tolov'])
#         if tolov < 1000:
#             tolov *= 1000
#         kurs = request.form['kurs']
#         oy = request.form['oy']
#         izoh = request.form.get('izoh', '')
#         admin = request.form['admin']
#         oqituvchi = request.form['oqituvchi']
#         tolov_turi = request.form['tolov_turi']
#         vaqt = datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%Y-%m-%d %H:%M:%S')

#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute('''
#             INSERT INTO tolovlar (ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt, tolov_turi)
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#         ''', (ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt, tolov_turi))
#         con.commit()
#         con.close()

#         message = (
#             f"💳 *Yangi to‘lov kiritildi!*\n\n"
#             f"👤 Ismi: {ismi}\n"
#             f"💰 To‘lov: {tolov:,} so‘m\n"
#             f"📚 Kurs: {kurs} ({oy} oyi)\n"
#             f"💳 To‘lov turi: {tolov_turi}\n"
#             f"👨‍🏫 O‘qituvchi: {oqituvchi}\n"
#             f"🛠 Admin: {admin}\n"
#             f"💬 Izoh: {izoh or 'Yo‘q'}\n"
#             f"🕒 Sana: {vaqt}"
#         )

#         for admin_id in ADMIN_CHAT_IDS:
#             try:
#                 requests.get(
#                     f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
#                     params={
#                         "chat_id": admin_id,
#                         "text": message,
#                         "parse_mode": "Markdown"
#                     }
#                 )
#             except Exception as e:
#                 print(f"Xabar yuborishda xatolik: {e}")

#         return redirect(url_for('index'))

#     today = datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%Y-%m-%d')
#     con = sqlite3.connect(DB_PATH)
#     cur = con.cursor()
#     cur.execute('''
#         SELECT ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt, tolov_turi
#         FROM tolovlar
#         WHERE date(vaqt) = ?
#         ORDER BY vaqt DESC
#     ''', (today,))
#     tolovlar = cur.fetchall()
#     con.close()

#     return render_template('index.html', tolovlar=tolovlar)


# @app.route('/download_excel')
# def download_excel():
#     con = sqlite3.connect(DB_PATH)
#     df = pd.read_sql_query("SELECT * FROM tolovlar ORDER BY vaqt DESC", con)
#     con.close()
#     if df.empty:
#         return "Bazadan ma'lumot topilmadi."
#     file_path = "tolovlar.xlsx"
#     df.to_excel(file_path, index=False)
#     return send_file(file_path, as_attachment=True)


# # ---------- TELEGRAM BOT QISMI ----------

# async def start(update: Update, context: CallbackContext):
#     user_id = update.effective_chat.id
#     if user_id not in ADMIN_CHAT_IDS:
#         await update.message.reply_text("Siz admin emassiz.")
#         return

#     keyboard = [
#         [InlineKeyboardButton("📅 Bugungi to‘lovlar", callback_data="today_report")],
#         [InlineKeyboardButton("📊 Oylik to‘lovlar", callback_data="oylik_menyu")]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await update.message.reply_text("Xush kelibsiz, admin! Tanlang:", reply_markup=reply_markup)


# async def handle_callback(update: Update, context: CallbackContext):
#     query = update.callback_query
#     await query.answer()
#     user_id = query.message.chat.id

#     if user_id not in ADMIN_CHAT_IDS:
#         await query.edit_message_text("Siz admin emassiz.")
#         return

#     if query.data == "today_report":
#         today = datetime.now(pytz.timezone('Asia/Tashkent')).date().isoformat()
#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute("SELECT tolov_turi, SUM(tolov) FROM tolovlar WHERE DATE(vaqt) = ? GROUP BY tolov_turi", (today,))
#         rows = cur.fetchall()
#         con.close()

#         if not rows:
#             await query.edit_message_text(
#                 f"📅 *{today}* kuni hech qanday to‘lov yo‘q.",
#                 parse_mode="Markdown"
#             )
#             return

#         naqd = sum(row[1] for row in rows if row[0].lower() == "naqd")
#         karta = sum(row[1] for row in rows if row[0].lower() == "click" or row[0].lower() == "karta")
#         jami = naqd + karta

#         await query.edit_message_text(
#             f"🗓 *{today}* uchun to‘lovlar:\n\n"
#             f"💵 Naqd: {naqd:,} so‘m\n"
#             f"💳 Karta: {karta:,} so‘m\n"
#             f"📊 Jami: {jami:,} so‘m",
#             parse_mode="Markdown"
#         )

#     elif query.data == "oylik_menyu":
#         oylar = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
#                  "Iyul", "Avgust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr"]
#         keyboard = [[InlineKeyboardButton(f"🗓 {oy}", callback_data=f"month_{oy.lower()}")] for oy in oylar]
#         reply_markup = InlineKeyboardMarkup(keyboard)
#         await query.edit_message_text("Oy bo‘yicha hisobotni tanlang:", reply_markup=reply_markup)

#     elif query.data.startswith("month_"):
#         oy_nomi = query.data.replace("month_", "")
#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute("SELECT tolov_turi, SUM(tolov) FROM tolovlar WHERE lower(oy) = lower(?) GROUP BY tolov_turi", (oy_nomi,))
#         rows = cur.fetchall()
#         con.close()

#         if not rows:
#             await query.edit_message_text(f"🗓 {oy_nomi.capitalize()} oyi uchun to‘lovlar topilmadi.")
#             return

#         naqd = sum(row[1] for row in rows if row[0].lower() == "naqd")
#         karta = sum(row[1] for row in rows if row[0].lower() in ["click", "karta"])
#         jami = naqd + karta

#         await query.edit_message_text(
#             f"🗓 *{oy_nomi.capitalize()}* oyi uchun to‘lovlar:\n\n"
#             f"💵 Naqd: {naqd:,} so‘m\n"
#             f"💳 Karta: {karta:,} so‘m\n"
#             f"📊 Jami: {jami:,} so‘m",
#             parse_mode="Markdown"
#         )


# async def run_bot():
#     app_bot = Application.builder().token(BOT_TOKEN).build()
#     app_bot.add_handler(CommandHandler("start", start))
#     app_bot.add_handler(CallbackQueryHandler(handle_callback))
#     print("✅ Bot ishga tushdi.")
#     await app_bot.run_polling()


# if __name__ == '__main__':
#     import threading
#     nest_asyncio.apply()
#     threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000)).start()
#     asyncio.run(run_bot())

import os
import sqlite3
import pandas as pd
import asyncio
import pytz
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
)
from flask import Flask
import nest_asyncio

nest_asyncio.apply()

# --- BOT SOZLAMALARI ---
BOT_TOKEN = '7935396412:AAHJS61QJTdHtaf7pNrwtEqNdxZrWgapOR4'
ADMIN_CHAT_IDS = [6855997739, 266123144, 1657599027, 6449680789]
DB_PATH = 'crm.db'
UZ_TZ = pytz.timezone('Asia/Tashkent')

app = Flask(__name__)


# --- DATABASE UCHUN FUNKSIYA ---
def get_payments(filter_type="today"):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM payments", conn)
    conn.close()

    if df.empty:
        return pd.DataFrame()

    df["date"] = pd.to_datetime(df["date"])
    today = datetime.now(UZ_TZ).date()

    if filter_type == "today":
        df = df[df["date"].dt.date == today]
    elif filter_type == "month":
        df = df[df["date"].dt.month == today.month]

    return df


# --- EXCEL HISOBOT YARATISH ---
def create_excel_report(df, report_type="today"):
    if df.empty:
        return None

    today_str = datetime.now(UZ_TZ).strftime("%Y-%m-%d")
    file_name = f"Tolovlar_{today_str if report_type == 'today' else 'Oylik'}.xlsx"

    # To‘lov summalarini hisoblash
    total_cash = df[df["type"] == "Naqd"]["amount"].sum()
    total_card = df[df["type"] == "Karta"]["amount"].sum()
    total_all = df["amount"].sum()

    # Excelga yozish
    with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='To‘lovlar')
        summary = pd.DataFrame({
            'Hisobot': ['Naqd', 'Karta', 'Jami'],
            'Miqdor': [total_cash, total_card, total_all]
        })
        summary.to_excel(writer, index=False, sheet_name='Jami')

    return file_name


# --- BUGUNGI HISOBOT YUBORISH ---
async def send_daily_report(application: Application):
    df = get_payments("today")
    if df.empty:
        message = "Bugungi to‘lovlar mavjud emas."
        for admin_id in ADMIN_CHAT_IDS:
            await application.bot.send_message(chat_id=admin_id, text=message)
        return

    file_path = create_excel_report(df, "today")
    for admin_id in ADMIN_CHAT_IDS:
        await application.bot.send_document(chat_id=admin_id, document=open(file_path, 'rb'),
                                            caption=f"📅 Bugungi to‘lovlar ({datetime.now(UZ_TZ).strftime('%Y-%m-%d')})")
    os.remove(file_path)


# --- OYLIK HISOBOT YUBORISH ---
async def send_monthly_report(application: Application):
    df = get_payments("month")
    if df.empty:
        message = "Bu oy uchun to‘lovlar mavjud emas."
        for admin_id in ADMIN_CHAT_IDS:
            await application.bot.send_message(chat_id=admin_id, text=message)
        return

    file_path = create_excel_report(df, "month")
    for admin_id in ADMIN_CHAT_IDS:
        await application.bot.send_document(chat_id=admin_id, document=open(file_path, 'rb'),
                                            caption=f"📊 Oylik to‘lovlar ({datetime.now(UZ_TZ).strftime('%B %Y')})")
    os.remove(file_path)


# --- /start BUYRUG‘I ---
async def start(update: Update, context: CallbackContext):
    df = get_payments("today")
    if df.empty:
        await update.message.reply_text("Bugungi to‘lovlar mavjud emas.")
        return

    file_path = create_excel_report(df, "today")
    await update.message.reply_document(open(file_path, 'rb'),
                                        caption=f"📅 Bugungi to‘lovlar ({datetime.now(UZ_TZ).strftime('%Y-%m-%d')})")
    os.remove(file_path)


# --- /oylik BUYRUG‘I ---
async def monthly(update: Update, context: CallbackContext):
    df = get_payments("month")
    if df.empty:
        await update.message.reply_text("Bu oy uchun to‘lovlar mavjud emas.")
        return

    file_path = create_excel_report(df, "month")
    await update.message.reply_document(open(file_path, 'rb'),
                                        caption=f"📊 Oylik to‘lovlar ({datetime.now(UZ_TZ).strftime('%B %Y')})")
    os.remove(file_path)


# --- 23:59 DA AVTOMATIK HISOBOT ---
async def scheduler(application: Application):
    while True:
        now = datetime.now(UZ_TZ)
        if now.hour == 23 and now.minute == 59:
            await send_daily_report(application)
            await asyncio.sleep(70)
        await asyncio.sleep(30)


# --- ASOSIY ISHLATISH ---
async def main():
    app_tg = Application.builder().token(BOT_TOKEN).build()

    app_tg.add_handler(CommandHandler("start", start))
    app_tg.add_handler(CommandHandler("oylik", monthly))

    asyncio.create_task(scheduler(app_tg))
    await app_tg.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
