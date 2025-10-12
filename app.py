# import os
# import sqlite3
# from datetime import datetime, time as dtime
# import pandas as pd
# import pytz
# import asyncio
# import nest_asyncio
# import requests
# from flask import Flask, render_template, request, redirect, url_for
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import (
#     Application,
#     CommandHandler,
#     CallbackContext,
#     CallbackQueryHandler,
# )

# app = Flask(__name__)
# DB_PATH = 'crm.db'
# BOT_TOKEN = '7935396412:AAFhVBQ1NNmw-giNGacreQkS71bsFlZAmM8'
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
#             f"💰 To‘lov: {tolov} so‘m\n"
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
#         cur.execute("SELECT * FROM tolovlar WHERE DATE(vaqt) = ?", (today,))
#         rows = cur.fetchall()
#         con.close()

#         if not rows:
#             await query.edit_message_text(
#                 f"📅 *{today}* kuni hech qanday to‘lov yo‘q. Excel fayl yaratilmadi.",
#                 parse_mode="Markdown"
#             )
#             return

#         total_sum = sum(row[2] for row in rows)
#         await query.edit_message_text(
#             f"📅 *{today}* kuni jami to‘lov: *{total_sum:,}* so‘m",
#             parse_mode="Markdown"
#         )

#         df = pd.DataFrame(
#             rows,
#             columns=['id', 'ismi', 'tolov', 'kurs', 'oy', 'izoh', 'admin', 'oqituvchi', 'vaqt', 'tolov_turi']
#         )

#         os.makedirs("reports", exist_ok=True)

#         for oy in df['oy'].unique():
#             oy_df = df[df['oy'] == oy].copy()

#             # ✅ Oxirida Jami, Naqd, Klik qo‘shish
#             oy_df['tolov_turi'] = oy_df['tolov_turi'].astype(str).str.lower()

#             jami_row = pd.DataFrame({
#                 'id': [''],
#                 'ismi': ['Jami to‘lov'],
#                 'tolov': [oy_df['tolov'].sum()],
#                 'kurs': [''],
#                 'oy': [''],
#                 'izoh': [''],
#                 'admin': [''],
#                 'oqituvchi': [''],
#                 'vaqt': [''],
#                 'tolov_turi': ['']
#             })

#             naqd_sum = oy_df.loc[oy_df['tolov_turi'] == 'naqd', 'tolov'].sum()
#             klik_sum = oy_df.loc[oy_df['tolov_turi'].isin(['klik', 'click']), 'tolov'].sum()

#             naqd_row = pd.DataFrame({
#                 'id': [''],
#                 'ismi': ['Naqd'],
#                 'tolov': [naqd_sum],
#                 'kurs': [''],
#                 'oy': [''],
#                 'izoh': [''],
#                 'admin': [''],
#                 'oqituvchi': [''],
#                 'vaqt': [''],
#                 'tolov_turi': ['']
#             })
#             klik_row = pd.DataFrame({
#                 'id': [''],
#                 'ismi': ['Klik'],
#                 'tolov': [klik_sum],
#                 'kurs': [''],
#                 'oy': [''],
#                 'izoh': [''],
#                 'admin': [''],
#                 'oqituvchi': [''],
#                 'vaqt': [''],
#                 'tolov_turi': ['']
#             })

#             oy_df = pd.concat([oy_df, jami_row, naqd_row, klik_row], ignore_index=True)

#             file_path = f"reports/hisobot_{today}_{oy}.xlsx"

#             try:
#                 oy_df.to_excel(file_path, index=False)
#                 for admin_id in ADMIN_CHAT_IDS:
#                     try:
#                         with open(file_path, 'rb') as f:
#                             await context.bot.send_document(
#                                 chat_id=admin_id,
#                                 document=f,
#                                 caption=f"{oy.capitalize()} oyi - {today}"
#                             )
#                     except Exception as e:
#                         print(f"Failed to send document to admin {admin_id}: {e}")
#             except Exception as e:
#                 print(f"Failed to generate Excel for {oy}: {e}")
#                 await context.bot.send_message(
#                     chat_id=user_id,
#                     text=f"Excel fayl yaratishda xato: {oy}"
#                 )

#     elif query.data == "oylik_menyu":
#         oylar = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
#                  "Iyul", "Avgust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr"]
#         keyboard = [[InlineKeyboardButton(f"🗓 {oy}", callback_data=f"month_{oy.lower()}")] for oy in oylar]
#         reply_markup = InlineKeyboardMarkup(keyboard)
#         await query.edit_message_text("Oy bo‘yicha hisobotni tanlang:", reply_markup=reply_markup)

#     # elif query.data.startswith("month_"):
#     #     oy_nomi = query.data.replace("month_", "")
#     #     con = sqlite3.connect(DB_PATH)
#     #     cur = con.cursor()
#     #     cur.execute("SELECT tolov FROM tolovlar WHERE lower(oy) = ?", (oy_nomi,))
#     #     rows = cur.fetchall()
#     #     con.close()

#     #     if not rows:
#     #         await query.edit_message_text(f"{oy_nomi.capitalize()} oyi uchun to‘lovlar topilmadi.")
#     #         return

#     #     total_sum = sum(row[0] for row in rows)
#     #     await query.edit_message_text(
#     #         f"🗓 *{oy_nomi.capitalize()}* oyi uchun jami to‘lov: *{total_sum:,}* so‘m",
#     #         parse_mode="Markdown"
#     #     )
#     elif query.data.startswith("month_"):
#         oy_nomi = query.data.replace("month_", "")
#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute("SELECT tolov, tolov_turi FROM tolovlar WHERE lower(oy) = ?", (oy_nomi,))
#         rows = cur.fetchall()
#         con.close()

#         if not rows:
#             await query.edit_message_text(f"{oy_nomi.capitalize()} oyi uchun to‘lovlar topilmadi.")
#             return

#         # Hisoblash
#         jami_sum = sum(row[0] for row in rows)
#         naqd_sum = sum(row[0] for row in rows if str(row[1]).lower() == "naqd")
#         karta_sum = sum(row[0] for row in rows if str(row[1]).lower() in ["klik", "click", "karta", "card"])

#         text = (
#             f"🗓 *{oy_nomi.capitalize()}* oyi uchun to‘lovlar:\n\n"
#             f"💵 Naqd: {naqd_sum:,} so‘m\n"
#             f"💳 Karta: {karta_sum:,} so‘m\n"
#             f"📊 Jami: {jami_sum:,} so‘m"
#         )

#         await query.edit_message_text(text, parse_mode="Markdown")



# async def send_daily_report(context: CallbackContext):
#     today = datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%Y-%m-%d')
#     con = sqlite3.connect(DB_PATH)
#     df = pd.read_sql_query("SELECT * FROM tolovlar WHERE DATE(vaqt) = ?", con, params=(today,))
#     con.close()

#     if df.empty:
#         for admin_id in ADMIN_CHAT_IDS:
#             try:
#                 await context.bot.send_message(chat_id=admin_id, text=f"📅 {today} kuni hech qanday to‘lov bo‘lmadi.")
#             except Exception as e:
#                 print(f"Failed to send empty report message to admin {admin_id}: {e}")
#     else:
#         os.makedirs("reports", exist_ok=True)
#         for oy in df['oy'].unique():
#             oy_df = df[df['oy'] == oy].copy()

#             # ✅ Oxirida Jami, Naqd, Klik qo‘shish
#             oy_df['tolov_turi'] = oy_df['tolov_turi'].astype(str).str.lower()

#             jami_row = pd.DataFrame({
#                 'id': [''],
#                 'ismi': ['Jami to‘lov'],
#                 'tolov': [oy_df['tolov'].sum()],
#                 'kurs': [''],
#                 'oy': [''],
#                 'izoh': [''],
#                 'admin': [''],
#                 'oqituvchi': [''],
#                 'vaqt': [''],
#                 'tolov_turi': ['']
#             })

#             naqd_sum = oy_df.loc[oy_df['tolov_turi'] == 'naqd', 'tolov'].sum()
#             klik_sum = oy_df.loc[oy_df['tolov_turi'].isin(['klik', 'click']), 'tolov'].sum()

#             naqd_row = pd.DataFrame({
#                 'id': [''],
#                 'ismi': ['Naqd'],
#                 'tolov': [naqd_sum],
#                 'kurs': [''],
#                 'oy': [''],
#                 'izoh': [''],
#                 'admin': [''],
#                 'oqituvchi': [''],
#                 'vaqt': [''],
#                 'tolov_turi': ['']
#             })
#             klik_row = pd.DataFrame({
#                 'id': [''],
#                 'ismi': ['Klik'],
#                 'tolov': [klik_sum],
#                 'kurs': [''],
#                 'oy': [''],
#                 'izoh': [''],
#                 'admin': [''],
#                 'oqituvchi': [''],
#                 'vaqt': [''],
#                 'tolov_turi': ['']
#             })

#             oy_df = pd.concat([oy_df, jami_row, naqd_row, klik_row], ignore_index=True)

#             file_path = f"reports/hisobot_{today}_{oy}.xlsx"

#             try:
#                 oy_df.to_excel(file_path, index=False)
#                 for admin_id in ADMIN_CHAT_IDS:
#                     try:
#                         with open(file_path, 'rb') as f:
#                             await context.bot.send_document(
#                                 chat_id=admin_id,
#                                 document=f,
#                                 caption=f"{oy.capitalize()} oyi - {today}"
#                             )
#                     except Exception as e:
#                         print(f"Failed to send document to admin {admin_id}: {e}")
#             except Exception as e:
#                 print(f"Failed to generate Excel for {oy}: {e}")
#                 for admin_id in ADMIN_CHAT_IDS:
#                     try:
#                         await context.bot.send_message(
#                             chat_id=admin_id,
#                             text=f"Excel fayl yaratishda xato: {oy}"
#                         )
#                     except Exception as e:
#                         print(f"Failed to send error message to admin {admin_id}: {e}")


# async def run_bot():
#     app_bot = Application.builder().token(BOT_TOKEN).build()
#     app_bot.add_handler(CommandHandler("start", start))
#     app_bot.add_handler(CallbackQueryHandler(handle_callback))
#     app_bot.job_queue.run_daily(send_daily_report, time=dtime(hour=23, minute=59, tzinfo=pytz.timezone('Asia/Tashkent')))

#     print("✅ Bot ishga tushdi.")
#     await app_bot.run_polling()


# if __name__ == '__main__':
#     import threading
#     nest_asyncio.apply()
#     threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000)).start()
#     asyncio.run(run_bot())


import os
import sqlite3
from datetime import datetime, time as dtime
import pandas as pd
import pytz
import asyncio
import nest_asyncio
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
)

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # Sessiyalar uchun kerak

DB_PATH = 'crm.db'
BOT_TOKEN = '7935396412:AAFhVBQ1NNmw-giNGacreQkS71bsFlZAmM8'
ADMIN_CHAT_IDS = [6855997739, 266123144, 1657599027, 6449680789]


# === Database yaratish ===
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
                vaqt TEXT NOT NULL,
                tolov_turi TEXT
            )
        ''')
        con.commit()
        con.close()


init_db()


# === LOGIN SAHIFA ===
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "muhammad" and password == "magistr2024":
            session['logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash("Login yoki parol xato!", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')


# === LOGOUT ===
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# === ADMIN PANEL SAHIFA ===
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT * FROM tolovlar ORDER BY vaqt DESC")
    tolovlar = cur.fetchall()
    con.close()

    return render_template('admin.html', tolovlar=tolovlar)


# === TO‘LOVNI TAHRIRLASH ===
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_tolov(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    if request.method == 'POST':
        ismi = request.form['ismi']
        tolov = int(request.form['tolov'])
        kurs = request.form['kurs']
        oy = request.form['oy']
        izoh = request.form['izoh']
        admin = request.form['admin']
        oqituvchi = request.form['oqituvchi']
        tolov_turi = request.form['tolov_turi']

        cur.execute('''
            UPDATE tolovlar
            SET ismi=?, tolov=?, kurs=?, oy=?, izoh=?, admin=?, oqituvchi=?, tolov_turi=?
            WHERE id=?
        ''', (ismi, tolov, kurs, oy, izoh, admin, oqituvchi, tolov_turi, id))
        con.commit()
        con.close()
        flash("To‘lov ma’lumoti yangilandi!", "success")
        return redirect(url_for('admin_panel'))

    cur.execute("SELECT * FROM tolovlar WHERE id=?", (id,))
    tolov = cur.fetchone()
    con.close()
    return render_template('edit.html', tolov=tolov)


# === TO‘LOVNI O‘CHIRISH ===
@app.route('/delete/<int:id>')
def delete_tolov(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("DELETE FROM tolovlar WHERE id=?", (id,))
    con.commit()
    con.close()
    flash("To‘lov o‘chirildi!", "warning")
    return redirect(url_for('admin_panel'))


# === OYLIK TO‘LOVLARNI O‘ZGARTIRISH (BARCHA OY NOMLARINI BIRGA) ===
@app.route('/update_month', methods=['POST'])
def update_month():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    old_month = request.form['old_month'].lower()
    new_month = request.form['new_month']

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("UPDATE tolovlar SET oy=? WHERE lower(oy)=?", (new_month, old_month))
    con.commit()
    con.close()
    flash(f"{old_month.capitalize()} oyi {new_month} ga o‘zgartirildi!", "info")
    return redirect(url_for('admin_panel'))


# === INDEX SAHIFA (to‘lov kiritish) ===
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ismi = request.form['ismi']
        tolov = int(request.form['tolov'])
        if tolov < 1000:
            tolov *= 1000
        kurs = request.form['kurs']
        oy = request.form['oy']
        izoh = request.form.get('izoh', '')
        admin = request.form['admin']
        oqituvchi = request.form['oqituvchi']
        tolov_turi = request.form['tolov_turi']
        vaqt = datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%Y-%m-%d %H:%M:%S')

        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute('''
            INSERT INTO tolovlar (ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt, tolov_turi)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt, tolov_turi))
        con.commit()
        con.close()

        # Telegram xabari
        message = (
            f"💳 *Yangi to‘lov kiritildi!*\n\n"
            f"👤 Ismi: {ismi}\n"
            f"💰 To‘lov: {tolov:,} so‘m\n"
            f"📚 Kurs: {kurs} ({oy} oyi)\n"
            f"💳 To‘lov turi: {tolov_turi}\n"
            f"👨‍🏫 O‘qituvchi: {oqituvchi}\n"
            f"🛠 Admin: {admin}\n"
            f"💬 Izoh: {izoh or 'Yo‘q'}\n"
            f"🕒 Sana: {vaqt}"
        )

        for admin_id in ADMIN_CHAT_IDS:
            try:
                requests.get(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    params={
                        "chat_id": admin_id,
                        "text": message,
                        "parse_mode": "Markdown"
                    }
                )
            except Exception as e:
                print(f"Xabar yuborishda xatolik: {e}")

        return redirect(url_for('index'))

    today = datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%Y-%m-%d')
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute('''
        SELECT ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt, tolov_turi
        FROM tolovlar
        WHERE date(vaqt) = ?
        ORDER BY vaqt DESC
    ''', (today,))
    tolovlar = cur.fetchall()
    con.close()
    return render_template('index.html', tolovlar=tolovlar)


# === TELEGRAM BOT QISMI (o‘zgarmagan) ===
async def start(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    if user_id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("Siz admin emassiz.")
        return

    keyboard = [
        [InlineKeyboardButton("📅 Bugungi to‘lovlar", callback_data="today_report")],
        [InlineKeyboardButton("📊 Oylik to‘lovlar", callback_data="oylik_menyu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Xush kelibsiz, admin! Tanlang:", reply_markup=reply_markup)


async def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = query.message.chat.id

    if user_id not in ADMIN_CHAT_IDS:
        await query.edit_message_text("Siz admin emassiz.")
        return

    if query.data == "today_report":
        today = datetime.now(pytz.timezone('Asia/Tashkent')).date().isoformat()
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT * FROM tolovlar WHERE DATE(vaqt) = ?", (today,))
        rows = cur.fetchall()
        con.close()

        if not rows:
            await query.edit_message_text(
                f"📅 *{today}* kuni hech qanday to‘lov yo‘q. Excel fayl yaratilmadi.",
                parse_mode="Markdown"
            )
            return

        total_sum = sum(row[2] for row in rows)
        await query.edit_message_text(
            f"📅 *{today}* kuni jami to‘lov: *{total_sum:,}* so‘m",
            parse_mode="Markdown"
        )

        df = pd.DataFrame(
            rows,
            columns=['id', 'ismi', 'tolov', 'kurs', 'oy', 'izoh', 'admin', 'oqituvchi', 'vaqt', 'tolov_turi']
        )

        os.makedirs("reports", exist_ok=True)

        for oy in df['oy'].unique():
            oy_df = df[df['oy'] == oy].copy()

            # ✅ Oxirida Jami, Naqd, Klik qo‘shish
            oy_df['tolov_turi'] = oy_df['tolov_turi'].astype(str).str.lower()

            jami_row = pd.DataFrame({
                'id': [''],
                'ismi': ['Jami to‘lov'],
                'tolov': [oy_df['tolov'].sum()],
                'kurs': [''],
                'oy': [''],
                'izoh': [''],
                'admin': [''],
                'oqituvchi': [''],
                'vaqt': [''],
                'tolov_turi': ['']
            })

            naqd_sum = oy_df.loc[oy_df['tolov_turi'] == 'naqd', 'tolov'].sum()
            klik_sum = oy_df.loc[oy_df['tolov_turi'].isin(['klik', 'click']), 'tolov'].sum()

            naqd_row = pd.DataFrame({
                'id': [''],
                'ismi': ['Naqd'],
                'tolov': [naqd_sum],
                'kurs': [''],
                'oy': [''],
                'izoh': [''],
                'admin': [''],
                'oqituvchi': [''],
                'vaqt': [''],
                'tolov_turi': ['']
            })
            klik_row = pd.DataFrame({
                'id': [''],
                'ismi': ['Klik'],
                'tolov': [klik_sum],
                'kurs': [''],
                'oy': [''],
                'izoh': [''],
                'admin': [''],
                'oqituvchi': [''],
                'vaqt': [''],
                'tolov_turi': ['']
            })

            oy_df = pd.concat([oy_df, jami_row, naqd_row, klik_row], ignore_index=True)

            file_path = f"reports/hisobot_{today}_{oy}.xlsx"

            try:
                oy_df.to_excel(file_path, index=False)
                for admin_id in ADMIN_CHAT_IDS:
                    try:
                        with open(file_path, 'rb') as f:
                            await context.bot.send_document(
                                chat_id=admin_id,
                                document=f,
                                caption=f"{oy.capitalize()} oyi - {today}"
                            )
                    except Exception as e:
                        print(f"Failed to send document to admin {admin_id}: {e}")
            except Exception as e:
                print(f"Failed to generate Excel for {oy}: {e}")
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"Excel fayl yaratishda xato: {oy}"
                )

    elif query.data == "oylik_menyu":
        oylar = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
                 "Iyul", "Avgust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr"]
        keyboard = [[InlineKeyboardButton(f"🗓 {oy}", callback_data=f"month_{oy.lower()}")] for oy in oylar]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Oy bo‘yicha hisobotni tanlang:", reply_markup=reply_markup)

    # elif query.data.startswith("month_"):
    #     oy_nomi = query.data.replace("month_", "")
    #     con = sqlite3.connect(DB_PATH)
    #     cur = con.cursor()
    #     cur.execute("SELECT tolov FROM tolovlar WHERE lower(oy) = ?", (oy_nomi,))
    #     rows = cur.fetchall()
    #     con.close()

    #     if not rows:
    #         await query.edit_message_text(f"{oy_nomi.capitalize()} oyi uchun to‘lovlar topilmadi.")
    #         return

    #     total_sum = sum(row[0] for row in rows)
    #     await query.edit_message_text(
    #         f"🗓 *{oy_nomi.capitalize()}* oyi uchun jami to‘lov: *{total_sum:,}* so‘m",
    #         parse_mode="Markdown"
    #     )
    elif query.data.startswith("month_"):
        oy_nomi = query.data.replace("month_", "")
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT tolov, tolov_turi FROM tolovlar WHERE lower(oy) = ?", (oy_nomi,))
        rows = cur.fetchall()
        con.close()

        if not rows:
            await query.edit_message_text(f"{oy_nomi.capitalize()} oyi uchun to‘lovlar topilmadi.")
            return

        # Hisoblash
        jami_sum = sum(row[0] for row in rows)
        naqd_sum = sum(row[0] for row in rows if str(row[1]).lower() == "naqd")
        karta_sum = sum(row[0] for row in rows if str(row[1]).lower() in ["klik", "click", "karta", "card"])

        text = (
            f"🗓 *{oy_nomi.capitalize()}* oyi uchun to‘lovlar:\n\n"
            f"💵 Naqd: {naqd_sum:,} so‘m\n"
            f"💳 Karta: {karta_sum:,} so‘m\n"
            f"📊 Jami: {jami_sum:,} so‘m"
        )

        await query.edit_message_text(text, parse_mode="Markdown")



async def send_daily_report(context: CallbackContext):
    today = datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%Y-%m-%d')
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM tolovlar WHERE DATE(vaqt) = ?", con, params=(today,))
    con.close()

    if df.empty:
        for admin_id in ADMIN_CHAT_IDS:
            try:
                await context.bot.send_message(chat_id=admin_id, text=f"📅 {today} kuni hech qanday to‘lov bo‘lmadi.")
            except Exception as e:
                print(f"Failed to send empty report message to admin {admin_id}: {e}")
    else:
        os.makedirs("reports", exist_ok=True)
        for oy in df['oy'].unique():
            oy_df = df[df['oy'] == oy].copy()

            # ✅ Oxirida Jami, Naqd, Klik qo‘shish
            oy_df['tolov_turi'] = oy_df['tolov_turi'].astype(str).str.lower()

            jami_row = pd.DataFrame({
                'id': [''],
                'ismi': ['Jami to‘lov'],
                'tolov': [oy_df['tolov'].sum()],
                'kurs': [''],
                'oy': [''],
                'izoh': [''],
                'admin': [''],
                'oqituvchi': [''],
                'vaqt': [''],
                'tolov_turi': ['']
            })

            naqd_sum = oy_df.loc[oy_df['tolov_turi'] == 'naqd', 'tolov'].sum()
            klik_sum = oy_df.loc[oy_df['tolov_turi'].isin(['klik', 'click']), 'tolov'].sum()

            naqd_row = pd.DataFrame({
                'id': [''],
                'ismi': ['Naqd'],
                'tolov': [naqd_sum],
                'kurs': [''],
                'oy': [''],
                'izoh': [''],
                'admin': [''],
                'oqituvchi': [''],
                'vaqt': [''],
                'tolov_turi': ['']
            })
            klik_row = pd.DataFrame({
                'id': [''],
                'ismi': ['Klik'],
                'tolov': [klik_sum],
                'kurs': [''],
                'oy': [''],
                'izoh': [''],
                'admin': [''],
                'oqituvchi': [''],
                'vaqt': [''],
                'tolov_turi': ['']
            })

            oy_df = pd.concat([oy_df, jami_row, naqd_row, klik_row], ignore_index=True)

            file_path = f"reports/hisobot_{today}_{oy}.xlsx"

            try:
                oy_df.to_excel(file_path, index=False)
                for admin_id in ADMIN_CHAT_IDS:
                    try:
                        with open(file_path, 'rb') as f:
                            await context.bot.send_document(
                                chat_id=admin_id,
                                document=f,
                                caption=f"{oy.capitalize()} oyi - {today}"
                            )
                    except Exception as e:
                        print(f"Failed to send document to admin {admin_id}: {e}")
            except Exception as e:
                print(f"Failed to generate Excel for {oy}: {e}")
                for admin_id in ADMIN_CHAT_IDS:
                    try:
                        await context.bot.send_message(
                            chat_id=admin_id,
                            text=f"Excel fayl yaratishda xato: {oy}"
                        )
                    except Exception as e:
                        print(f"Failed to send error message to admin {admin_id}: {e}")

async def run_bot():
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CallbackQueryHandler(lambda u, c: None))  # qisqartirish uchun

    print("✅ Bot ishga tushdi.")
    await app_bot.run_polling()


if __name__ == '__main__':
    import threading
    nest_asyncio.apply()
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=True)).start()
    asyncio.run(run_bot())
