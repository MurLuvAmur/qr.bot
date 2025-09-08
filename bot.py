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

# Обработчик ввода цвета
async def received_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    color = update.message.text
    
    # Простая валидация цвета
    if not re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color) and color not in ['black', 'red', 'blue', 'green', 'yellow', 'purple']:
        await update.message.reply_text("Неверный формат цвета. Попробуйте снова:")
        return TYPING_COLOR
    
    user_settings[user_id]['color'] = color
    await update.message.reply_text(
        f"Цвет установлен: {color}",
        reply_markup=markup
    )
    return CHOOSING

# Обработчик ввода размера
async def received_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    try:
        size = int(update.message.text)
        if size < 5 or size > 20:
            await update.message.reply_text("Размер должен быть между 5 и 20. Попробуйте снова:")
            return TYPING_SIZE
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число. Попробуйте снова:")
        return TYPING_SIZE
    
    user_settings[user_id]['size'] = size
    await update.message.reply_text(
        f"Размер установлен: {size}",
        reply_markup=markup
    )
    return CHOOSING

# Обработчик добавления логотипа
async def received_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if update.message.photo:
        # Получаем самое качественное фото
        photo_file = await update.message.photo[-1].get_file()
        buffer = BytesIO()
        await photo_file.download_to_memory(buffer)
        buffer.seek(0)
        
        user_settings[user_id]['logo'] = buffer
        await update.message.reply_text(
            "Логотип добавлен!",
            reply_markup=markup
        )
    else:
        await update.message.reply_text(
            "Пожалуйста, отправьте изображение. Попробуйте снова:",
            reply_markup=ReplyKeyboardRemove()
        )
        return ADDING_LOGO
    
    return CHOOSING

# Функция для добавления логотипа к QR-коду
def add_logo_to_qr(qr_buffer, logo_buffer, output_size=200):
    # Открываем QR-код и логотип
    qr_img = Image.open(qr_buffer).convert("RGBA")
    logo_img = Image.open(logo_buffer).convert("RGBA")
    
    # Масштабируем логотип
    logo_size = output_size // 4
    logo_img = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
    
    # Создаем круглую маску для логотипа
    mask = Image.new('L', (logo_size, logo_size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, logo_size, logo_size), fill=255)
    
    # Применяем маску к логотипу
    logo_img.putalpha(mask)
    
    # Позиционируем логотип в центре QR-кода
    pos = ((qr_img.width - logo_size) // 2, (qr_img.height - logo_size) // 2)
    
    # Накладываем логотип на QR-код
    qr_img.paste(logo_img, pos, logo_img)
    
    # Сохраняем результат
    result_buffer = BytesIO()
    qr_img.save(result_buffer, format='PNG')
    result_buffer.seek(0)
    
    return result_buffer


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
