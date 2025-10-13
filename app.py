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
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'  # Change this to a strong, random key
DB_PATH = 'crm.db'
BOT_TOKEN = '7935396412:AAFhVBQ1NNmw-giNGacreQkS71bsFlZAmM8'
ADMIN_CHAT_IDS = [6855997739, 266123144, 1657599027, 6449680789]

# Admin credentials
ADMIN_USERNAME = 'muhammad'
ADMIN_PASSWORD_HASH = generate_password_hash('magistr2024')

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tolovlar (
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

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Bu sahifaga kirish uchun avval tizimga kiring.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['logged_in'] = True
            flash('Muvaffaqiyatli tizimga kirdingiz!', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Noto‘g‘ri foydalanuvchi nomi yoki parol', 'danger')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    flash('Tizimdan chiqdingiz.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/panel')
@login_required
def admin_panel():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute('''
        SELECT id, ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt, tolov_turi
        FROM tolovlar
        ORDER BY vaqt DESC
    ''')
    tolovlar = cur.fetchall()
    con.close()
    return render_template('admin_panel.html', tolovlar=tolovlar)

@app.route('/admin/edit/<int:tolov_id>', methods=['GET', 'POST'])
@login_required
def edit_tolov(tolov_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
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
        vaqt = datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%Y-%m-%d %H:%M:%S') # Update timestamp

        cur.execute('''
            UPDATE tolovlar
            SET ismi = ?, tolov = ?, kurs = ?, oy = ?, izoh = ?, admin = ?, oqituvchi = ?, vaqt = ?, tolov_turi = ?
            WHERE id = ?
        ''', (ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt, tolov_turi, tolov_id))
        con.commit()
        con.close()
        flash('To‘lov muvaffaqiyatli tahrirlandi!', 'success')
        return redirect(url_for('admin_panel'))
    else:
        cur.execute('SELECT * FROM tolovlar WHERE id = ?', (tolov_id,))
        tolov = cur.fetchone()
        con.close()
        if tolov:
            # Convert tuple to dictionary for easier access in template
            tolov_dict = {
                'id': tolov[0],
                'ismi': tolov[1],
                'tolov': tolov[2],
                'kurs': tolov[3],
                'oy': tolov[4],
                'izoh': tolov[5],
                'admin': tolov[6],
                'oqituvchi': tolov[7],
                'vaqt': tolov[8],
                'tolov_turi': tolov[9]
            }
            return render_template('edit_tolov.html', tolov=tolov_dict)
        else:
            flash('To‘lov topilmadi.', 'danger')
            return redirect(url_for('admin_panel'))

@app.route('/admin/delete/<int:tolov_id>', methods=['POST'])
@login_required
def delete_tolov(tolov_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute('DELETE FROM tolovlar WHERE id = ?', (tolov_id,))
    con.commit()
    con.close()
    flash('To‘lov muvaffaqiyatli o‘chirildi!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/monthly_summary', methods=['GET'])
@login_required
def monthly_summary():
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT oy, tolov, tolov_turi FROM tolovlar", con)
    con.close()

    if df.empty:
        flash("Hech qanday to'lovlar topilmadi.", "info")
        return render_template('monthly_summary.html', monthly_data={})

    # Ensure 'tolov_turi' is string and lowercase for consistent filtering
    df['tolov_turi'] = df['tolov_turi'].astype(str).str.lower()

    # Aggregate by month and payment type
    monthly_data = {}
    for oy in df['oy'].unique():
        month_df = df[df['oy'] == oy]
        total = month_df['tolov'].sum()
        naqd = month_df[month_df['tolov_turi'] == 'naqd']['tolov'].sum()
        karta = month_df[month_df['tolov_turi'].isin(['klik', 'click', 'karta', 'card'])]['tolov'].sum()
        monthly_data[oy] = {
            'total': total,
            'naqd': naqd,
            'karta': karta
        }

    return render_template('monthly_summary.html', monthly_data=monthly_data)

@app.route('/admin/edit_monthly_total', methods=['GET', 'POST'])
@login_required
def edit_monthly_total():
    flash('Oylik jami summani o\'zgartirish funksiyasi to\'lovlarni birma-bir tahrirlash orqali amalga oshiriladi. Bu yerdan alohida o\'zgartirish mumkin emas.', 'info')
    return redirect(url_for('monthly_summary'))

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

        message = (
            f"💳 *Yangi to‘lov kiritildi!*\n\n"
            f"👤 Ismi: {ismi}\n"
            f"💰 To‘lov: {tolov} so‘m\n"
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
    app_bot.add_handler(CallbackQueryHandler(handle_callback))
    app_bot.job_queue.run_daily(send_daily_report, time=dtime(hour=23, minute=59, tzinfo=pytz.timezone('Asia/Tashkent')))

    print("✅ Bot ishga tushdi.")
    await app_bot.run_polling()


if __name__ == '__main__':
    import threading
    nest_asyncio.apply()
    # Create the 'templates' directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)

    # Create the HTML templates
    # admin_login.html
    with open('templates/admin_login.html', 'w', encoding='utf-8') as f:
        f.write('''
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Kirish</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header text-center">
                        <h4>Admin Kirish</h4>
                    </div>
                    <div class="card-body">
                        {% with messages = get_flashed_messages(with_categories=true) %}
                            {% if messages %}
                                {% for category, message in messages %}
                                    <div class="alert alert-{{ category }}">{{ message }}</div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        <form method="POST" action="{{ url_for('admin_login') }}">
                            <div class="form-group">
                                <label for="username">Foydalanuvchi nomi:</label>
                                <input type="text" class="form-control" id="username" name="username" required>
                            </div>
                            <div class="form-group">
                                <label for="password">Parol:</label>
                                <input type="password" class="form-control" id="password" name="password" required>
                            </div>
                            <button type="submit" class="btn btn-primary btn-block">Kirish</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
        ''')

    # admin_panel.html
    with open('templates/admin_panel.html', 'w', encoding='utf-8') as f:
        f.write('''
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        .table-responsive {
            max-height: 80vh;
            overflow-y: auto;
        }
        th, td {
            white-space: nowrap;
        }
    </style>
</head>
<body>
    <div class="container-fluid mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2>Admin Panel - Barcha To‘lovlar</h2>
            <div>
                <a href="{{ url_for('monthly_summary') }}" class="btn btn-info mr-2">Oylik hisobotlar</a>
                <a href="{{ url_for('admin_logout') }}" class="btn btn-danger">Chiqish</a>
            </div>
        </div>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <div class="table-responsive">
            <table class="table table-striped table-bordered table-hover">
                <thead class="thead-dark">
                    <tr>
                        <th>ID</th>
                        <th>Ismi</th>
                        <th>To‘lov</th>
                        <th>Kurs</th>
                        <th>Oy</th>
                        <th>Izoh</th>
                        <th>Admin</th>
                        <th>O‘qituvchi</th>
                        <th>Vaqt</th>
                        <th>To‘lov turi</th>
                        <th>Harakatlar</th>
                    </tr>
                </thead>
                <tbody>
                    {% for tolov in tolovlar %}
                        <tr>
                            <td>{{ tolov[0] }}</td>
                            <td>{{ tolov[1] }}</td>
                            <td>{{ "{:,.0f}".format(tolov[2]) }} so‘m</td>
                            <td>{{ tolov[3] }}</td>
                            <td>{{ tolov[4] }}</td>
                            <td>{{ tolov[5] or 'Yo‘q' }}</td>
                            <td>{{ tolov[6] }}</td>
                            <td>{{ tolov[7] }}</td>
                            <td>{{ tolov[8] }}</td>
                            <td>{{ tolov[9] or 'Noma’lum' }}</td>
                            <td>
                                <a href="{{ url_for('edit_tolov', tolov_id=tolov[0]) }}" class="btn btn-sm btn-warning">Tahrirlash</a>
                                <form action="{{ url_for('delete_tolov', tolov_id=tolov[0]) }}" method="POST" style="display:inline-block;">
                                    <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Haqiqatan ham ushbu to‘lovni o‘chirmoqchimisiz?');">O‘chirish</button>
                                </form>
                            </td>
                        </tr>
                    {% else %}
                        <tr>
                            <td colspan="11" class="text-center">Hech qanday to‘lov topilmadi.</td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
        ''')

    # edit_tolov.html
    with open('templates/edit_tolov.html', 'w', encoding='utf-8') as f:
        f.write('''
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>To‘lovni Tahrirlash</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2>To‘lovni Tahrirlash</h2>
            <a href="{{ url_for('admin_panel') }}" class="btn btn-secondary">Orqaga</a>
        </div>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <div class="card">
            <div class="card-body">
                <form method="POST" action="{{ url_for('edit_tolov', tolov_id=tolov.id) }}">
                    <div class="form-group">
                        <label for="ismi">Ismi:</label>
                        <input type="text" class="form-control" id="ismi" name="ismi" value="{{ tolov.ismi }}" required>
                    </div>
                    <div class="form-group">
                        <label for="tolov">To‘lov (so‘mda):</label>
                        <input type="number" class="form-control" id="tolov" name="tolov" value="{{ tolov.tolov }}" required min="1">
                    </div>
                    <div class="form-group">
                        <label for="kurs">Kurs:</label>
                        <input type="text" class="form-control" id="kurs" name="kurs" value="{{ tolov.kurs }}" required>
                    </div>
                    <div class="form-group">
                        <label for="oy">Oy:</label>
                        <select class="form-control" id="oy" name="oy" required>
                            {% set oylar = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun", "Iyul", "Avgust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr"] %}
                            {% for oy in oylar %}
                                <option value="{{ oy }}" {% if tolov.oy == oy %}selected{% endif %}>{{ oy }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="izoh">Izoh:</label>
                        <textarea class="form-control" id="izoh" name="izoh" rows="3">{{ tolov.izoh }}</textarea>
                    </div>
                    <div class="form-group">
                        <label for="admin">Admin:</label>
                        <input type="text" class="form-control" id="admin" name="admin" value="{{ tolov.admin }}" required>
                    </div>
                    <div class="form-group">
                        <label for="oqituvchi">O‘qituvchi:</label>
                        <input type="text" class="form-control" id="oqituvchi" name="oqituvchi" value="{{ tolov.oqituvchi }}" required>
                    </div>
                    <div class="form-group">
                        <label for="tolov_turi">To‘lov turi:</label>
                        <select class="form-control" id="tolov_turi" name="tolov_turi" required>
                            <option value="Naqd" {% if tolov.tolov_turi == 'Naqd' %}selected{% endif %}>Naqd</option>
                            <option value="Plastik" {% if tolov.tolov_turi == 'Plastik' %}selected{% endif %}>Plastik</option>
                            <option value="Klik" {% if tolov.tolov_turi == 'Klik' %}selected{% endif %}>Klik</option>
                            <option value="Payme" {% if tolov.tolov_turi == 'Payme' %}selected{% endif %}>Payme</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary">Saqlash</button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
        ''')

    # monthly_summary.html
    with open('templates/monthly_summary.html', 'w', encoding='utf-8') as f:
        f.write('''
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Oylik hisobotlar</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2>Oylik To‘lov Hisobotlari</h2>
            <a href="{{ url_for('admin_panel') }}" class="btn btn-secondary">Orqaga</a>
        </div>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% if monthly_data %}
            <div class="table-responsive">
                <table class="table table-striped table-bordered table-hover">
                    <thead class="thead-dark">
                        <tr>
                            <th>Oy</th>
                            <th>Jami To‘lov</th>
                            <th>Naqd To‘lov</th>
                            <th>Karta Orqali To‘lov</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for oy, data in monthly_data.items() %}
                            <tr>
                                <td>{{ oy }}</td>
                                <td>{{ "{:,.0f}".format(data.total) }} so‘m</td>
                                <td>{{ "{:,.0f}".format(data.naqd) }} so‘m</td>
                                <td>{{ "{:,.0f}".format(data.karta) }} so‘m</td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        {% else %}
            <p class="text-center">Hali hech qanday oylik to‘lov ma’lumotlari yo‘q.</p>
        {% endif %}
    </div>
</body>
</html>
        ''')

    # index.html (main payment entry form, unchanged from original but good to have)
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write('''
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>To'lov kiritish</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        .table-responsive {
            max-height: 50vh; /* Adjust as needed */
            overflow-y: auto;
        }
        th, td {
            white-space: nowrap;
        }
    </style>
</head>
<body>
    <div class="container-fluid mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2>Yangi to'lov kiritish</h2>
            <a href="{{ url_for('admin_login') }}" class="btn btn-primary">Admin Panelga kirish</a>
        </div>

        <div class="row">
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        Yangi to'lov formasi
                    </div>
                    <div class="card-body">
                        <form method="POST">
                            <div class="form-group">
                                <label for="ismi">Ismi:</label>
                                <input type="text" class="form-control" id="ismi" name="ismi" required>
                            </div>
                            <div class="form-group">
                                <label for="tolov">To'lov (so'mda, minglarda kiritish mumkin, masalan: 500 = 500.000):</label>
                                <input type="number" class="form-control" id="tolov" name="tolov" required min="1">
                            </div>
                            <div class="form-group">
                                <label for="kurs">Kurs:</label>
                                <input type="text" class="form-control" id="kurs" name="kurs" required>
                            </div>
                            <div class="form-group">
                                <label for="oy">Oy:</label>
                                <select class="form-control" id="oy" name="oy" required>
                                    <option value="Yanvar">Yanvar</option>
                                    <option value="Fevral">Fevral</option>
                                    <option value="Mart">Mart</option>
                                    <option value="Aprel">Aprel</option>
                                    <option value="May">May</option>
                                    <option value="Iyun">Iyun</option>
                                    <option value="Iyul">Iyul</option>
                                    <option value="Avgust">Avgust</option>
                                    <option value="Sentyabr">Sentyabr</option>
                                    <option value="Oktyabr">Oktyabr</option>
                                    <option value="Noyabr">Noyabr</option>
                                    <option value="Dekabr">Dekabr</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="izoh">Izoh (ixtiyoriy):</label>
                                <textarea class="form-control" id="izoh" name="izoh" rows="2"></textarea>
                            </div>
                            <div class="form-group">
                                <label for="admin">Admin:</label>
                                <input type="text" class="form-control" id="admin" name="admin" required>
                            </div>
                            <div class="form-group">
                                <label for="oqituvchi">O'qituvchi:</label>
                                <input type="text" class="form-control" id="oqituvchi" name="oqituvchi" required>
                            </div>
                            <div class="form-group">
                                <label for="tolov_turi">To'lov turi:</label>
                                <select class="form-control" id="tolov_turi" name="tolov_turi" required>
                                    <option value="Naqd">Naqd</option>
                                    <option value="Plastik">Plastik</option>
                                    <option value="Klik">Klik</option>
                                    <option value="Payme">Payme</option>
                                </select>
                            </div>
                            <button type="submit" class="btn btn-primary btn-block">To'lovni kiritish</button>
                        </form>
                    </div>
                </div>
            </div>
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        Bugungi to'lovlar ({{ datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%Y-%m-%d') }})
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped table-bordered table-hover">
                                <thead class="thead-dark">
                                    <tr>
                                        <th>Ismi</th>
                                        <th>To'lov</th>
                                        <th>Kurs</th>
                                        <th>Oy</th>
                                        <th>Izoh</th>
                                        <th>Admin</th>
                                        <th>O'qituvchi</th>
                                        <th>Vaqt</th>
                                        <th>To'lov turi</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for tolov in tolovlar %}
                                        <tr>
                                            <td>{{ tolov[0] }}</td>
                                            <td>{{ "{:,.0f}".format(tolov[1]) }} so'm</td>
                                            <td>{{ tolov[2] }}</td>
                                            <td>{{ tolov[3] }}</td>
                                            <td>{{ tolov[4] or 'Yo‘q' }}</td>
                                            <td>{{ tolov[5] }}</td>
                                            <td>{{ tolov[6] }}</td>
                                            <td>{{ tolov[7] }}</td>
                                            <td>{{ tolov[8] or 'Noma’lum' }}</td>
                                        </tr>
                                    {% else %}
                                        <tr>
                                            <td colspan="9" class="text-center">Bugun hech qanday to'lov kiritilmagan.</td>
                                        </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
        ''')


    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000)).start()
    asyncio.run(run_bot())
