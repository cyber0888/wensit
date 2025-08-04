import json
import os
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes, CallbackQueryHandler

PHONE, NAME, SURNAME, FATHER_NAME, REGION, DISTRICT, VILLAGE, CHECK_SUBSCRIPTION = range(8)

DATA_FILE = "userss.json"
CHANNEL_USERNAME = "@PROGRAM_CREATORR"  # Kanal username '@' bilan

def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)

async def check_channel_subscription(bot, user_id: int):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "creator", "administrator"]
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_id_str = str(user_id)
    users = load_users()

    if user_id_str in users and "phone" in users[user_id_str]:
        # Foydalanuvchi ro'yxatdan o'tgan, kanalga obuna ekanligini tekshiramiz
        is_subscribed = await check_channel_subscription(context.bot, user_id)
        if is_subscribed:
            await update.message.reply_text("Siz allaqachon ro'yxatdan o'tgansiz!")
            await update.message.reply_text(
                "Tayyor! Endi pastdagi xabarni 10 ta odamga tarqating. Hammasi avtomatik tasdiqlanadi.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Xabarni tarqatish", url="https://t.me/PROGRAM_CREATORR/32")]
                ])
            )
            return ConversationHandler.END
        else:
            # Kanalga obuna bo'lmagan
            await update.message.reply_text(
                "Siz kanalimizga obuna bo‘lmadingiz. Iltimos, kanalga obuna bo‘ling va kanalga obuna ekanligingizni tekshirish uchun /start ni bosing.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Kanalga obuna bo‘lish", url="https://t.me/PROGRAM_CREATORR")]
                ])
            )
            return ConversationHandler.END
    else:
        # Ro'yxatdan o'tmagan foydalanuvchi uchun
        await update.message.reply_text(
            "Salom! Ushbu botdan foydalanish uchun ro'yxatdan o'ting.",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Telefon raqamni ulashish", request_contact=True)]], resize_keyboard=True)
        )
        return PHONE

async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    user_id = str(update.effective_user.id)
    if contact:
        users = load_users()
        users[user_id] = {"phone": contact.phone_number}
        save_users(users)
        await update.message.reply_text(
            "Muvaffaqiyatli ro'yxatdan o'tildi! Tanlovda qatnashish uchun pastdagi tugmani bosing.",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Tanlovda qatnashish")]], resize_keyboard=True)
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text("Iltimos, telefon raqamingizni ulashing.")
        return PHONE

async def participate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_users()
    required_fields = ["phone", "name", "surname", "father_name", "region", "district", "village"]
    if not all(field in users.get(user_id, {}) for field in required_fields):
        await update.message.reply_text("Ismingizni kiriting:")
        return NAME
    else:
        # Ro'yxatdan o'tgan, kanalga obuna ekanligini tekshirish uchun start ga yo'naltirish mumkin,
        # ammo hozir shunchaki tugaydi
        await update.message.reply_text(
            "Siz allaqachon ro'yxatdan o'tgansiz! Tanlovda qatnashish uchun pastdagi tugmani bosing."
        )
        return ConversationHandler.END

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_users()
    users[user_id] = users.get(user_id, {})
    users[user_id]["name"] = update.message.text
    save_users(users)
    await update.message.reply_text("Familiyangizni kiriting:")
    return SURNAME

async def surname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_users()
    users[user_id]["surname"] = update.message.text
    save_users(users)
    await update.message.reply_text("Otangizning ismini kiriting:")
    return FATHER_NAME

async def father_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_users()
    users[user_id]["father_name"] = update.message.text
    save_users(users)
    await update.message.reply_text("Viloyatingizni kiriting:")
    return REGION

async def region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_users()
    users[user_id]["region"] = update.message.text
    save_users(users)
    await update.message.reply_text("Tumaningizni kiriting:")
    return DISTRICT

async def district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_users()
    users[user_id]["district"] = update.message.text
    save_users(users)
    await update.message.reply_text("Qishloqingizni kiriting (agar shaharda yashasangiz, '-' yuboring):")
    return VILLAGE

async def village(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_users()
    users[user_id]["village"] = update.message.text
    save_users(users)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Kanalga obuna bo'lganimni tasdiqlayman", callback_data="check_subscription")]
    ])

    await update.message.reply_text(
        "Iltimos, kanalga obuna bo'ling https://t.me/PROGRAM_CREATORR va Tasdiqlash uchun pastdagi tugmani bosing:",
        reply_markup=keyboard
    )
    return CHECK_SUBSCRIPTION

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    is_subscribed = await check_channel_subscription(context.bot, user_id)
    if is_subscribed:
        await query.edit_message_text(
            "Tayyor! Endi pastdagi xabarni 10 ta odamga tarqating. Hammasi avtomatik tasdiqlanadi.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Xabarni tarqatish", url="https://t.me/PROGRAM_CREATORR/32")]
            ])
        )
        return ConversationHandler.END
    else:
        await query.edit_message_text(
            "Siz kanalimizga obuna bo‘lmadingiz. Iltimos, kanalga obuna bo‘ling va kanalga obuna ekanligingizni tekshirish uchun /start ni bosing.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Kanalga obuna bo‘lish", url="https://t.me/PROGRAM_CREATORR")]
            ])
        )
        return CHECK_SUBSCRIPTION

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ro'yxatdan o'tish bekor qilindi.",
        reply_markup=ReplyKeyboardMarkup([], resize_keyboard=True)
    )
    return ConversationHandler.END

def main():
    application = Application.builder().token("7963168800:AAGHBrL5we5cefHtxkqFHuN86CH8tyJMyLk").build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.TEXT & filters.Regex("^Tanlovda qatnashish$"), participate),
        ],
        states={
            PHONE: [MessageHandler(filters.CONTACT, phone)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, surname)],
            FATHER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, father_name)],
            REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND, region)],
            DISTRICT: [MessageHandler(filters.TEXT & ~filters.COMMAND, district)],
            VILLAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, village)],
            CHECK_SUBSCRIPTION: [CallbackQueryHandler(check_subscription, pattern="^check_subscription$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == "__main__":
    main()
