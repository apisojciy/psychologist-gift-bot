import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)

# Логування (для налагодження)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Дані
YOUR_USERNAME = "andriy_pisotskiy"
psychologists = [
    ("Ткаченко Юлія Леонідівна", "https://doc.ua/ua/doctor/kiev/22001-yuliya-tkachenko/about"),
    ("Ольга Сергієнко", "https://k-s.org.ua/branches/team/olga-sergiyenko/"),
    ("Шкварок Наталія Борисівна", "https://uccbt.com.ua/specialists/shkvarok-nataliya-borysivna/")
]

# Етапи діалогу
CHOOSING, TYPING_CUSTOM = range(2)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Готова розпочати", callback_data="start_course")]]
    await update.message.reply_text("Привіт! Я бот для психологічного подарунка 🌿", reply_markup=InlineKeyboardMarkup(keyboard))

# Натиснуто "Готова розпочати"
async def start_course_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    return await show_psychologists(update, context)

# Показати варіанти психологів
async def show_psychologists(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton(name, url=url, callback_data=f"choose_{i}")] for i, (name, url) in enumerate(psychologists)
    ]
    buttons.append([InlineKeyboardButton("Інший варіант", callback_data="custom")])
    buttons.append([InlineKeyboardButton("🔁 Змінити вибір", callback_data="change")]) if context.user_data.get("chosen") else None

    if update.callback_query:
        await update.callback_query.edit_message_text("Оберіть психолога:", reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await update.message.reply_text("Оберіть психолога:", reply_markup=InlineKeyboardMarkup(buttons))
    return CHOOSING

# Обробка вибору
async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("choose_"):
        index = int(query.data.split("_")[1])
        name, url = psychologists[index]
        text = f"👤 Вибрано: {name}\n🔗 {url}"
        context.user_data["chosen"] = text

        await notify_sender(context, update.effective_user, text)
        await query.edit_message_text("Дякуємо за вибір! Найближчим часом надамо деталі сеансу 😊")

        return ConversationHandler.END

    elif query.data == "custom":
        await query.edit_message_text("Введіть ім’я або посилання на свого психолога:")
        return TYPING_CUSTOM

    elif query.data == "change":
        return await show_psychologists(update, context)

# Обробка введеного іншого варіанту
async def handle_custom_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"👤 Вибрано (свій варіант): {update.message.text}"
    context.user_data["chosen"] = text

    await notify_sender(context, update.effective_user, text)
    await update.message.reply_text("Дякуємо! Найближчим часом надамо деталі сеансу 😊")
    return ConversationHandler.END

# Надіслати повідомлення дарувальнику
async def notify_sender(context: ContextTypes.DEFAULT_TYPE, user, text):
    await context.bot.send_message(chat_id=YOUR_USERNAME, text=f"🎁 Вибір від @{user.username or user.first_name}:\n{text}")

# Основна функція
def main():
    app = ApplicationBuilder().token("7588127606:AAGscvK5SeIdZ3Qsx_oNzR4cK0A6njFD9mM").build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_course_callback, pattern="^start_course$")],
        states={
            CHOOSING: [CallbackQueryHandler(handle_choice)],
            TYPING_CUSTOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_text)],
        },
        fallbacks=[],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    app.run_polling()

if __name__ == "__main__":
    main()
