# from flask import Flask, render_template, request, redirect, url_for
# import sqlite3
# from datetime import datetime
# import os

# app = Flask(__name__)
# DB_PATH = 'crm.db'

# def init_db():
#     if not os.path.exists(DB_PATH):
#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute('''
#         CREATE TABLE payments (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             student_name TEXT NOT NULL,
#             amount INTEGER NOT NULL,
#             course TEXT NOT NULL,
#             month TEXT NOT NULL,
#             notes TEXT,
#             admin TEXT NOT NULL,
#             teacher TEXT NOT NULL,
#             timestamp TEXT NOT NULL
#         )
#         ''')
#         con.commit()
#         con.close()

# init_db()

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         # Form'dan ma'lumotlar
#         student = request.form['student_name']
#         amount  = int(request.form['amount'])
#         course  = request.form['course']
#         month   = request.form['month']
#         notes   = request.form.get('notes', '')
#         admin   = request.form['admin']        # yangi maydon
#         teacher = request.form['teacher']      # yangi maydon
#         ts      = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#         # Bazaga yozish
#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute('''
#             INSERT INTO payments
#             (student_name, amount, course, month, notes, admin, teacher, timestamp)
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#         ''', (student, amount, course, month, notes, admin, teacher, ts))
#         con.commit()
#         con.close()

#         return redirect(url_for('index'))

#     # GET: bugungi to‘lovlarni o‘qish
#     today = datetime.now().strftime('%Y-%m-%d')
#     con = sqlite3.connect(DB_PATH)
#     cur = con.cursor()
#     cur.execute('''
#         SELECT student_name, amount, course, month, notes, admin, teacher, timestamp
#         FROM payments
#         WHERE date(timestamp) = ?
#         ORDER BY timestamp DESC
#     ''', (today,))
#     payments = cur.fetchall()
#     con.close()

#     return render_template('index.html', payments=payments)

# if __name__ == '__main__':
#     app.run(debug=True)

# import os
# import sqlite3
# from datetime import datetime, date, time as dtime
# import pandas as pd
# import asyncio
# import nest_asyncio

# from flask import Flask, render_template, request, redirect, url_for
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import (
#     Application,
#     CommandHandler,
#     CallbackContext,
#     CallbackQueryHandler,
# )

# # --- Flask sozlamalari ---
# app = Flask(__name__)
# DB_PATH = 'crm.db'

# def init_db():
#     if not os.path.exists(DB_PATH):
#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute('''
#         CREATE TABLE payments (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             student_name TEXT NOT NULL,
#             amount INTEGER NOT NULL,
#             course TEXT NOT NULL,
#             month TEXT NOT NULL,
#             notes TEXT,
#             admin TEXT NOT NULL,
#             teacher TEXT NOT NULL,
#             timestamp TEXT NOT NULL
#         )
#         ''')
#         con.commit()
#         con.close()

# init_db()

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         student = request.form['student_name']
#         amount  = int(request.form['amount'])
#         course  = request.form['course']
#         month   = request.form['month']
#         notes   = request.form.get('notes', '')
#         admin   = request.form['admin']
#         teacher = request.form['teacher']
#         ts      = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute('''
#             INSERT INTO payments
#             (student_name, amount, course, month, notes, admin, teacher, timestamp)
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#         ''', (student, amount, course, month, notes, admin, teacher, ts))
#         con.commit()
#         con.close()

#         return redirect(url_for('index'))

#     today = datetime.now().strftime('%Y-%m-%d')
#     con = sqlite3.connect(DB_PATH)
#     cur = con.cursor()
#     cur.execute('''
#         SELECT student_name, amount, course, month, notes, admin, teacher, timestamp
#         FROM payments
#         WHERE date(timestamp) = ?
#         ORDER BY timestamp DESC
#     ''', (today,))
#     payments = cur.fetchall()
#     con.close()

#     return render_template('index.html', payments=payments)

# # --- Telegram bot sozlamalari ---
# BOT_TOKEN = '7687327295:AAGxG7xSVJWjEgx7YTghyhYUNDSttOPoHNM'
# ADMIN_CHAT_ID = 6855997739

# async def start(update: Update, context: CallbackContext):
#     keyboard = [[InlineKeyboardButton("📊 Bugungi to‘lovlar", callback_data="today_report")]]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await update.message.reply_text("Xush kelibsiz! Kerakli tugmani tanlang:", reply_markup=reply_markup)

# async def handle_callback(update: Update, context: CallbackContext):
#     query = update.callback_query
#     await query.answer()

#     if query.data == "today_report":
#         today = date.today().isoformat()
#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute("""
#             SELECT student_name, amount, course, month, admin, teacher, timestamp 
#             FROM payments 
#             WHERE DATE(timestamp) = ?
#         """, (today,))
#         rows = cur.fetchall()
#         con.close()

#         if not rows:
#             await query.edit_message_text("Bugun uchun to‘lovlar yo‘q.")
#             return

#         total_sum = sum(row[1] for row in rows)
#         message = f"📅 *{today}* sanasidagi to‘lovlar:\n\n"
#         for row in rows:
#             message += (
#                 f"👤 {row[0]}\n"
#                 f"💵 {row[1]} so‘m\n"
#                 f"📚 {row[2]} ({row[3]} oyi)\n"
#                 f"👨‍🏫 Uqituvchi: {row[5]}\n"
#                 f"🧾 Admin: {row[4]}\n"
#                 f"🕒 {row[6]}\n\n"
#             )
#         message += f"🔢 *Jami:* {total_sum} so‘m"

#         await query.edit_message_text(message, parse_mode="Markdown")

#         df = pd.DataFrame(rows, columns=["Talaba", "To‘lov", "Kurs", "Oy", "Admin", "Uqituvchi", "Vaqt"])
#         os.makedirs("reports", exist_ok=True)
#         file_path = f"reports/report_{today}.xlsx"
#         df.to_excel(file_path, index=False)

#         await context.bot.send_document(chat_id=query.message.chat.id, document=open(file_path, 'rb'))

# async def send_daily_report(context: CallbackContext):
#     con = sqlite3.connect(DB_PATH)
#     today = date.today().isoformat()
#     df = pd.read_sql_query("SELECT * FROM payments WHERE DATE(timestamp) = ?", con, params=(today,))
#     con.close()

#     if df.empty:
#         await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text="Bugun hech qanday to‘lov bo‘lmadi.")
#     else:
#         os.makedirs("reports", exist_ok=True)
#         file_path = f"reports/report_{today}.xlsx"
#         df.to_excel(file_path, index=False)
#         await context.bot.send_document(chat_id=ADMIN_CHAT_ID, document=open(file_path, 'rb'))

# async def run_bot():
#     app_bot = Application.builder().token(BOT_TOKEN).build()

#     app_bot.add_handler(CommandHandler("start", start))
#     app_bot.add_handler(CallbackQueryHandler(handle_callback))

#     app_bot.job_queue.run_daily(send_daily_report, time=dtime(hour=23, minute=59))

#     print("✅ Bot ishga tushdi.")
#     await app_bot.run_polling()

# if __name__ == '__main__':
#     import threading
#     import nest_asyncio
#     nest_asyncio.apply()

#     # Flask ilovasini alohida ipda ishga tushiramiz
#     threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False)).start()

#     # Telegram botni asyncio event loopda ishga tushuramiz
#     asyncio.run(run_bot())

# import os
# import sqlite3
# from datetime import datetime, date, time as dtime
# import pandas as pd
# import asyncio
# import nest_asyncio
# import pytz  # <-- pytz import qilindi

# from flask import Flask, render_template, request, redirect, url_for
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import (
#     Application,
#     CommandHandler,
#     CallbackContext,
#     CallbackQueryHandler,
# )

# # --- Flask sozlamalari ---
# app = Flask(__name__)
# DB_PATH = 'crm.db'

# uzbekistan_tz = pytz.timezone('Asia/Tashkent')  # O'zbekiston vaqt zonasi

# def init_db():
#     if not os.path.exists(DB_PATH):
#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute('''
#         CREATE TABLE payments (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             ismi TEXT NOT NULL,
#             tolov INTEGER NOT NULL,
#             kurs TEXT NOT NULL,
#             oy TEXT NOT NULL,
#             izoh TEXT,
#             admin TEXT NOT NULL,
#             oqituvchi TEXT NOT NULL,
#             vaqt TEXT NOT NULL
#         )
#         ''')
#         con.commit()
#         con.close()

# init_db()

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         ismi = request.form['student_name']
#         tolov  = int(request.form['amount'])
#         kurs  = request.form['course']
#         oy   = request.form['month']
#         izoh   = request.form.get('notes', '')
#         admin   = request.form['admin']
#         oqituvchi = request.form['teacher']
#         vaqt = datetime.now(uzbekistan_tz).strftime('%Y-%m-%d %H:%M:%S')  # O'zbekiston vaqti

#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute('''
#             INSERT INTO payments
#             (ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt)
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#         ''', (ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt))
#         con.commit()
#         con.close()

#         return redirect(url_for('index'))

#     today = datetime.now(uzbekistan_tz).strftime('%Y-%m-%d')  # O'zbekiston sanasi
#     con = sqlite3.connect(DB_PATH)
#     cur = con.cursor()
#     cur.execute('''
#         SELECT ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt
#         FROM payments
#         WHERE date(vaqt) = ?
#         ORDER BY vaqt DESC
#     ''', (today,))
#     payments = cur.fetchall()
#     con.close()

#     return render_template('index.html', payments=payments)

# # --- Telegram bot sozlamalari ---
# BOT_TOKEN = '7935396412:AAHJS61QJTdHtaf7pNrwtEqNdxZrWgapOR4'
# ADMINS = [6855997739, 266123144, 1657599027]  # Bu yerga admin chat_id larini qo'shish mumkin

# async def start(update: Update, context: CallbackContext):
#     keyboard = [[InlineKeyboardButton("📊 Bugungi to‘lovlar", callback_data="today_report")]]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await update.message.reply_text("Xush kelibsiz! Kerakli tugmani tanlang:", reply_markup=reply_markup)

# async def handle_callback(update: Update, context: CallbackContext):
#     query = update.callback_query
#     await query.answer()

#     if query.data == "today_report":
#         today = datetime.now(uzbekistan_tz).strftime('%Y-%m-%d')
#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute("""
#             SELECT ismi, tolov, kurs, oy, admin, oqituvchi, vaqt 
#             FROM payments 
#             WHERE DATE(vaqt) = ?
#         """, (today,))
#         rows = cur.fetchall()
#         con.close()

#         if not rows:
#             await query.edit_message_text("Bugun uchun to‘lovlar yo‘q.")
#             return

#         total_sum = sum(row[1] for row in rows)
#         message = f"📅 *{today}* sanasidagi to‘lovlar:\n\n"
#         for row in rows:
#             message += (
#                 f"👤 {row[0]}\n"
#                 f"💵 {row[1]} so‘m\n"
#                 f"📚 {row[2]} ({row[3]} oyi)\n"
#                 f"🧾 Admin: {row[4]}\n"
#                 f"👨‍🏫 O‘qituvchi: {row[5]}\n"
#                 f"🕒 {row[6]}\n\n"
#             )
#         message += f"🔢 *Jami:* {total_sum} so‘m"

#         await query.edit_message_text(message, parse_mode="Markdown")

#         df = pd.DataFrame(rows, columns=["Ismi", "To‘lov", "Kurs", "Oy", "Admin", "O‘qituvchi", "Vaqt"])
#         os.makedirs("reports", exist_ok=True)
#         file_path = f"reports/report_{today}.xlsx"
#         df.to_excel(file_path, index=False)

#         await context.bot.send_document(chat_id=query.message.chat.id, document=open(file_path, 'rb'))

# async def send_daily_report(context: CallbackContext):
#     con = sqlite3.connect(DB_PATH)
#     today = datetime.now(uzbekistan_tz).strftime('%Y-%m-%d')
#     df = pd.read_sql_query("SELECT * FROM payments WHERE DATE(vaqt) = ?", con, params=(today,))
#     con.close()

#     if df.empty:
#         for admin_id in ADMINS:
#             await context.bot.send_message(chat_id=admin_id, text="Bugun hech qanday to‘lov bo‘lmadi.")
#     else:
#         os.makedirs("reports", exist_ok=True)
#         file_path = f"reports/report_{today}.xlsx"
#         df.to_excel(file_path, index=False)
#         for admin_id in ADMINS:
#             await context.bot.send_document(chat_id=admin_id, document=open(file_path, 'rb'))

# async def run_bot():
#     app_bot = Application.builder().token(BOT_TOKEN).build()

#     app_bot.add_handler(CommandHandler("start", start))
#     app_bot.add_handler(CallbackQueryHandler(handle_callback))

#     # Kunlik hisobotni O'zbekiston vaqtida soat 23:59 da yuborish
#     app_bot.job_queue.run_daily(send_daily_report, time=dtime(hour=23, minute=59, tzinfo=uzbekistan_tz))

#     print("✅ Bot ishga tushdi.")
#     await app_bot.run_polling()

# if __name__ == '__main__':
#     import threading
#     import nest_asyncio
#     nest_asyncio.apply()

#     # Flask ilovasini alohida ipda ishga tushiramiz
#     threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False)).start()

#     # Telegram botni asyncio event loopda ishga tushuramiz
#     asyncio.run(run_bot())

# import os
# import sqlite3
# from datetime import datetime, date, time as dtime
# import pandas as pd
# import pytz
# import asyncio
# import nest_asyncio

# from flask import Flask, render_template, request, redirect, url_for
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import (
#     Application,
#     CommandHandler,
#     CallbackContext,
#     CallbackQueryHandler,
# )

# # --- Flask sozlamalari ---
# app = Flask(__name__)
# DB_PATH = 'crm.db'

# def init_db():
#     if not os.path.exists(DB_PATH):
#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute('''
#         CREATE TABLE tolovlar (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             ismi TEXT NOT NULL,
#             tolov INTEGER NOT NULL,
#             kurs TEXT NOT NULL,
#             oy TEXT NOT NULL,
#             izoh TEXT,
#             admin TEXT NOT NULL,
#             oqituvchi TEXT NOT NULL,
#             vaqt TEXT NOT NULL
#         )
#         ''')
#         con.commit()
#         con.close()

# init_db()

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         ismi = request.form['ismi']
#         tolov  = int(request.form['tolov'])
#         kurs  = request.form['kurs']
#         oy   = request.form['oy']
#         izoh   = request.form.get('izoh', '')
#         admin   = request.form['admin']
#         oqituvchi = request.form['oqituvchi']

#         # O'zbekiston vaqtini olish
#         uzbek_tz = pytz.timezone('Asia/Tashkent')
#         vaqt = datetime.now(uzbek_tz).strftime('%Y-%m-%d %H:%M:%S')

#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute('''
#             INSERT INTO tolovlar
#             (ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt)
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#         ''', (ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt))
#         con.commit()
#         con.close()

#         return redirect(url_for('index'))

#     today = datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%Y-%m-%d')
#     con = sqlite3.connect(DB_PATH)
#     cur = con.cursor()
#     cur.execute('''
#         SELECT ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt
#         FROM tolovlar
#         WHERE date(vaqt) = ?
#         ORDER BY vaqt DESC
#     ''', (today,))
#     tolovlar = cur.fetchall()
#     con.close()

#     return render_template('index.html', tolovlar=tolovlar)

# # --- Telegram bot sozlamalari ---
# BOT_TOKEN = '7935396412:AAHJS61QJTdHtaf7pNrwtEqNdxZrWgapOR4'  # Bot tokeningizni bu yerga yozing

# # Adminlar ro'yxati (chat_id lar)
# ADMIN_CHAT_IDS = [6855997739, 266123144, 1657599027]  # Bu yerga adminlar chat_id larini kiriting

# async def start(update: Update, context: CallbackContext):
#     user_id = update.effective_chat.id
#     if user_id not in ADMIN_CHAT_IDS:
#         await update.message.reply_text("Siz admin emassiz. Botdan foydalanish uchun ruxsat yo'q.")
#         return

#     keyboard = [[InlineKeyboardButton("📊 Bugungi to‘lovlar", callback_data="today_report")]]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await update.message.reply_text("Xush kelibsiz, admin! Kerakli tugmani tanlang:", reply_markup=reply_markup)

# async def handle_callback(update: Update, context: CallbackContext):
#     query = update.callback_query
#     await query.answer()

#     user_id = query.message.chat.id
#     if user_id not in ADMIN_CHAT_IDS:
#         await query.edit_message_text("Siz admin emassiz.")
#         return

#     if query.data == "today_report":
#         uzbek_tz = pytz.timezone('Asia/Tashkent')
#         today = datetime.now(uzbek_tz).date().isoformat()

#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute("""
#             SELECT ismi, tolov, kurs, oy, admin, oqituvchi, vaqt 
#             FROM tolovlar 
#             WHERE DATE(vaqt) = ?
#         """, (today,))
#         rows = cur.fetchall()
#         con.close()

#         if not rows:
#             await query.edit_message_text("Bugun uchun to‘lovlar yo‘q.")
#             return

#         total_sum = sum(row[1] for row in rows)
#         message = f"📅 *{today}* sanasidagi to‘lovlar:\n\n"
#         for row in rows:
#             message += (
#                 f"👤 {row[0]}\n"
#                 f"💵 {row[1]} so‘m\n"
#                 f"📚 {row[2]} ({row[3]} oyi)\n"
#                 f"🧾 Admin: {row[4]}\n"
#                 f"👨‍🏫 Oqituvchi: {row[5]}\n"
#                 f"🕒 {row[6]}\n\n"
#             )
#         message += f"🔢 *Jami:* {total_sum} so‘m"

#         await query.edit_message_text(message, parse_mode="Markdown")

#         # Excel hisobot yaratish
#         df = pd.DataFrame(rows, columns=["Ismi", "To'lov", "Kurs", "Oy", "Admin", "Oqituvchi", "Vaqt"])
#         os.makedirs("reports", exist_ok=True)
#         file_path = f"reports/hisobot_{today}.xlsx"
#         df.to_excel(file_path, index=False)

#         await context.bot.send_document(chat_id=user_id, document=open(file_path, 'rb'))

# async def send_daily_report(context: CallbackContext):
#     uzbek_tz = pytz.timezone('Asia/Tashkent')
#     today = datetime.now(uzbek_tz).date().isoformat()

#     con = sqlite3.connect(DB_PATH)
#     df = pd.read_sql_query("SELECT * FROM tolovlar WHERE DATE(vaqt) = ?", con, params=(today,))
#     con.close()

#     if df.empty:
#         for admin_id in ADMIN_CHAT_IDS:
#             await context.bot.send_message(chat_id=admin_id, text="Bugun hech qanday to‘lov bo‘lmadi.")
#     else:
#         os.makedirs("reports", exist_ok=True)
#         file_path = f"reports/hisobot_{today}.xlsx"
#         df.to_excel(file_path, index=False)
#         for admin_id in ADMIN_CHAT_IDS:
#             await context.bot.send_document(chat_id=admin_id, document=open(file_path, 'rb'))

# async def run_bot():
#     app_bot = Application.builder().token(BOT_TOKEN).build()

#     app_bot.add_handler(CommandHandler("start", start))
#     app_bot.add_handler(CallbackQueryHandler(handle_callback))

#     # Har kuni soat 23:59 da hisobot yuborish (O'zbekiston vaqti bilan)
#     app_bot.job_queue.run_daily(send_daily_report, time=dtime(hour=23, minute=59, tzinfo=pytz.timezone('Asia/Tashkent')))

#     print("✅ Bot ishga tushdi.")
#     await app_bot.run_polling()

# if __name__ == '__main__':
#     import threading
#     nest_asyncio.apply()

#     # Flask ilovasini alohida ipda ishga tushiramiz
#     threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False)).start()

#     # Telegram botni asyncio event loopda ishga tushuramiz
#     asyncio.run(run_bot())

import os
import sqlite3
from datetime import datetime, time as dtime
import pandas as pd
import pytz
import asyncio
import nest_asyncio

from flask import Flask, render_template, request, redirect, url_for
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
)

# --- Flask sozlamalari ---
app = Flask(__name__)
DB_PATH = 'crm.db'

def init_db():
    if not os.path.exists(DB_PATH):
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute('''
        CREATE TABLE tolovlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ismi TEXT NOT NULL,
            tolov INTEGER NOT NULL,
            kurs TEXT NOT NULL,
            oy TEXT NOT NULL,
            izoh TEXT,
            admin TEXT NOT NULL,
            oqituvchi TEXT NOT NULL,
            vaqt TEXT NOT NULL
        )
        ''')
        con.commit()
        con.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # HTML formadagi name atributlariga moslab olingan ma'lumotlar
        ismi = request.form['student_name']
        tolov  = int(request.form['amount'])
        kurs  = request.form['course']
        oy   = request.form['month']
        izoh   = request.form.get('notes', '')
        admin   = request.form['admin']
        oqituvchi = request.form['teacher']

        # O'zbekiston vaqtini olish
        uzbek_tz = pytz.timezone('Asia/Tashkent')
        vaqt = datetime.now(uzbek_tz).strftime('%Y-%m-%d %H:%M:%S')

        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute('''
            INSERT INTO tolovlar
            (ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt))
        con.commit()
        con.close()

        return redirect(url_for('index'))

    today = datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%Y-%m-%d')
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute('''
        SELECT ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt
        FROM tolovlar
        WHERE date(vaqt) = ?
        ORDER BY vaqt DESC
    ''', (today,))
    tolovlar = cur.fetchall()
    con.close()

    return render_template('index.html', tolovlar=tolovlar)

# --- Telegram bot sozlamalari ---
BOT_TOKEN = '7935396412:AAHJS61QJTdHtaf7pNrwtEqNdxZrWgapOR4'  # Bot tokeningizni shu yerga yozing

# Adminlar ro'yxati (chat_id lar)
ADMIN_CHAT_IDS = [6855997739, 266123144, 1657599027]  # Admin chat_id larini kiriting

async def start(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    if user_id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("Siz admin emassiz. Botdan foydalanish uchun ruxsat yo'q.")
        return

    keyboard = [[InlineKeyboardButton("📊 Bugungi to‘lovlar", callback_data="today_report")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Xush kelibsiz, admin! Kerakli tugmani tanlang:", reply_markup=reply_markup)

async def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    user_id = query.message.chat.id
    if user_id not in ADMIN_CHAT_IDS:
        await query.edit_message_text("Siz admin emassiz.")
        return

    if query.data == "today_report":
        uzbek_tz = pytz.timezone('Asia/Tashkent')
        today = datetime.now(uzbek_tz).date().isoformat()

        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("""
            SELECT ismi, tolov, kurs, oy, admin, oqituvchi, vaqt 
            FROM tolovlar 
            WHERE DATE(vaqt) = ?
        """, (today,))
        rows = cur.fetchall()
        con.close()

        if not rows:
            await query.edit_message_text("Bugun uchun to‘lovlar yo‘q.")
            return

        total_sum = sum(row[1] for row in rows)
        message = f"📅 *{today}* sanasidagi to‘lovlar:\n\n"
        for row in rows:
            message += (
                f"👤 {row[0]}\n"
                f"💵 {row[1]} so‘m\n"
                f"📚 {row[2]} ({row[3]} oyi)\n"
                f"🧾 Admin: {row[4]}\n"
                f"👨‍🏫 Oqituvchi: {row[5]}\n"
                f"🕒 {row[6]}\n\n"
            )
        message += f"🔢 *Jami:* {total_sum} so‘m"

        await query.edit_message_text(message, parse_mode="Markdown")

        # Excel hisobot yaratish
        df = pd.DataFrame(rows, columns=["Ismi", "To'lov", "Kurs", "Oy", "Admin", "Oqituvchi", "Vaqt"])
        os.makedirs("reports", exist_ok=True)
        file_path = f"reports/hisobot_{today}.xlsx"
        df.to_excel(file_path, index=False)

        await context.bot.send_document(chat_id=user_id, document=open(file_path, 'rb'))

async def send_daily_report(context: CallbackContext):
    uzbek_tz = pytz.timezone('Asia/Tashkent')
    today = datetime.now(uzbek_tz).date().isoformat()

    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM tolovlar WHERE DATE(vaqt) = ?", con, params=(today,))
    con.close()

    if df.empty:
        for admin_id in ADMIN_CHAT_IDS:
            await context.bot.send_message(chat_id=admin_id, text="Bugun hech qanday to‘lov bo‘lmadi.")
    else:
        os.makedirs("reports", exist_ok=True)
        file_path = f"reports/hisobot_{today}.xlsx"
        df.to_excel(file_path, index=False)
        for admin_id in ADMIN_CHAT_IDS:
            await context.bot.send_document(chat_id=admin_id, document=open(file_path, 'rb'))

async def run_bot():
    app_bot = Application.builder().token(BOT_TOKEN).build()

    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CallbackQueryHandler(handle_callback))

    # Har kuni soat 23:59 da hisobot yuborish (O'zbekiston vaqti bilan)
    app_bot.job_queue.run_daily(send_daily_report, time=dtime(hour=23, minute=59, tzinfo=pytz.timezone('Asia/Tashkent')))

    print("✅ Bot ishga tushdi.")
    await app_bot.run_polling()

if __name__ == '__main__':
    import threading
    nest_asyncio.apply()

    # Flask ilovasini alohida ipda ishga tushiramiz
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False)).start()

    # Telegram botni asyncio event loopda ishga tushuramiz
    asyncio.run(run_bot())
