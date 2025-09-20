# Telegram QR Code Generator Bot

Telegram-бот для создания кастомных QR-кодов с возможностью настройки цвета, размера и добавления логотипа.

## Возможности

- Генерация QR-кодов из текста или URL
- Настройка цвета QR-кода (HEX или название)
- Изменение размера QR-кода
- Добавление логотипа в центр QR-кода
- Интуитивный интерфейс с клавиатурой настроек

## Технологии

- Python 3.10+
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - асинхронный фреймворк для Telegram Bot API
- [segno](https://github.com/heuer/segno) - генерация QR-кодов
- [Pillow](https://github.com/python-pillow/Pillow) - работа с изображениями
- [python-dotenv](https://github.com/theskumar/python-dotenv) - загрузка переменных окружения

## Установка и запуск

Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```
Создайте виртуальное окружение и установите зависимости:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/MacOS
# или
venv\Scripts\activate  # для Windows
pip install -r requirements.txt
```
Создайте файл .env и добавьте токен бота:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```
Запустите бота:

```bash
python bot.py
```

Как использовать:
1. Начните общение с ботом через команду /start
2. Используйте меню для настройки параметров QR-кода:
3. Выберите цвет QR-кода
4. Настройте размер
5. Добавьте логотип
6. Просмотрите текущие настройки
7. Введите текст или URL для генерации QR-кода
8. Получите готовый QR-код с вашими настройками
