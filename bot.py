import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import segno
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import re
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем токен бота из переменных окружения
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Проверяем, что токен был загружен
if not TOKEN:
    raise ValueError("Токен бота не найден. Убедитесь, что он указан в .env файле")

# Состояния для ConversationHandler
CHOOSING, TYPING_COLOR, TYPING_SIZE, TYPING_TEXT, ADDING_LOGO = range(5)

# Хранение пользовательских настроек
user_settings = {}

# Клавиатура с основными опциями
reply_keyboard = [
    ["Цвет QR-кода", "Размер QR-кода"],
    ["Добавить логотип", "Показать настройки"],
    ["Сгенерировать QR-код"]
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    # Инициализируем настройки по умолчанию для пользователя
    user_settings[user_id] = {
        'color': 'black',
        'background': 'white',
        'size': 10,
        'logo': None
    }
    
    await update.message.reply_text(
        "Привет! Я бот для создания кастомных QR-кодов.\n"
        "Выбери опцию для настройки:",
        reply_markup=markup
    )
    return CHOOSING

# Обработчик выбора опции
async def regular_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data['choice'] = text
    user_id = update.message.from_user.id
    
    if text == "Цвет QR-кода":
        await update.message.reply_text(
            "Введите цвет в формате HEX (например, #FF5733) или название цвета на английском:",
            reply_markup=ReplyKeyboardRemove()
        )
        return TYPING_COLOR
    elif text == "Размер QR-кода":
        await update.message.reply_text(
            "Введите размер (от 5 до 20, где 10 - стандартный):",
            reply_markup=ReplyKeyboardRemove()
        )
        return TYPING_SIZE
    elif text == "Добавить логотип":
        await update.message.reply_text(
            "Отправьте изображение для использования в качестве логотипа:",
            reply_markup=ReplyKeyboardRemove()
        )
        return ADDING_LOGO
    elif text == "Показать настройки":
        settings = user_settings.get(user_id, {})
        await update.message.reply_text(
            f"Текущие настройки:\n"
            f"Цвет: {settings.get('color', 'black')}\n"
            f"Фон: {settings.get('background', 'white')}\n"
            f"Размер: {settings.get('size', 10)}\n"
            f"Логотип: {'Да' if settings.get('logo') else 'Нет'}",
            reply_markup=markup
        )
        return CHOOSING
    elif text == "Сгенерировать QR-код":
        await update.message.reply_text(
            "Введите текст или URL для кодирования в QR-код:",
            reply_markup=ReplyKeyboardRemove()
        )
        return TYPING_TEXT


# Основная функция
def main():
    # Создаем приложение и передаем токен
    application = Application.builder().token(TOKEN).build()
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_qr))
    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()