import telebot
from telebot import types

API_TOKEN = '6730091039:AAERw4eW0Gg6IQBvXsR0u7vg1c4I8fmsMWM'
CHANNEL_USERNAME = '@magistr_guliston'
ADMIN_ID = 685599739  # Admin ID

bot = telebot.TeleBot(API_TOKEN)

# post_id -> like count
post_likes = {}

# user_id -> list of liked post_ids
user_likes = {}


# --- Obunani tekshirish funksiyasi ---
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False


# --- Like tugmasi yaratish ---
def create_like_button(post_id):
    like_count = post_likes.get(post_id, 0)
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(f"👍 Like ({like_count})",
                                     callback_data=f"like|{post_id}")
    markup.add(btn)
    return markup


# --- /start ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "👋 Salom! Like bosish uchun kanalga obuna bo‘ling.")


# --- /admin_post --- (admin reply qilib yuboradi)
@bot.message_handler(commands=['admin_post'])
def admin_post(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "🚫 Siz admin emassiz.")

    if not message.reply_to_message:
        return bot.reply_to(
            message,
            "⛔ Avval postga reply qilib, /admin_post buyrug‘ini yozing.")

    caption = message.text[12:].strip() or "📢 Post"

    if message.reply_to_message.video:
        sent = bot.send_video(chat_id=CHANNEL_USERNAME,
                              video=message.reply_to_message.video.file_id,
                              caption=caption,
                              reply_markup=create_like_button(
                                  message.reply_to_message.message_id))
    elif message.reply_to_message.text:
        sent = bot.send_message(chat_id=CHANNEL_USERNAME,
                                text=message.reply_to_message.text,
                                reply_markup=create_like_button(
                                    message.reply_to_message.message_id))
    else:
        return bot.reply_to(
            message, "⛔ Faqat video yoki matnli xabar yuborish mumkin.")

    post_likes[sent.message_id] = 0
    bot.reply_to(message, "✅ Post kanalga yuborildi!")


# --- Like tugmasini bosish ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('like|'))
def handle_like(call):
    user_id = call.from_user.id
    post_id = int(call.data.split('|')[1])

    if not is_subscribed(user_id):
        return bot.answer_callback_query(
            call.id,
            f"❌ Like bosish uchun {CHANNEL_USERNAME} kanaliga obuna bo‘ling!",
            show_alert=True)

    if user_id in user_likes and post_id in user_likes[user_id]:
        return bot.answer_callback_query(call.id,
                                         "✅ Siz allaqachon like bosgansiz.")

    post_likes[post_id] = post_likes.get(post_id, 0) + 1
    user_likes.setdefault(user_id, []).append(post_id)

    new_markup = create_like_button(post_id)
    try:
        bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      reply_markup=new_markup)
    except:
        pass

    bot.answer_callback_query(call.id, "👍 Like qabul qilindi!")


# --- /edit_like 123 50 (admin uchun) ---
@bot.message_handler(commands=['edit_like'])
def edit_like(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "❌ Siz admin emassiz.")

    parts = message.text.split()
    if len(parts) != 3:
        return bot.reply_to(message,
                            "❗ Foydalanish: /edit_like POST_ID YANGI_SON")

    try:
        post_id = int(parts[1])
        new_count = int(parts[2])
        post_likes[post_id] = new_count

        bot.edit_message_reply_markup(chat_id=CHANNEL_USERNAME,
                                      message_id=post_id,
                                      reply_markup=create_like_button(post_id))

        bot.reply_to(message, f"✅ Like soni {new_count} ga yangilandi.")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Xatolik: {e}")


if __name__ == '__main__':
    bot.polling(none_stop=True)
