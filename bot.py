import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import segno
from io import BytesIO
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем токен бота из переменных окружения
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Проверяем, что токен был загружен
if not TOKEN:
    raise ValueError("Токен бота не найден. Убедитесь, что он указан в .env файле")

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь мне текст или ссылку, и я превращу их в QR-код."
    )

# Обработчик текстовых сообщений
async def generate_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        # Создаем QR-код
        qr = segno.make_qr(user_text)
        # Сохраняем QR-код в буфер памяти
        buffer = BytesIO()
        qr.save(buffer, kind="png", scale=10)
        buffer.seek(0)
        # Отправляем изображение пользователю
        await update.message.reply_photo(photo=buffer, caption="Вот твой QR-код!")
    except Exception as e:
        await update.message.reply_text("Что-то пошло не так. Попробуй еще раз.")

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