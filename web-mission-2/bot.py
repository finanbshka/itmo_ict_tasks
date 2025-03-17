import os
import requests
from io import BytesIO
from PIL import Image
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Конфигурация
TELEGRAM_BOT_TOKEN = "<YOUR_PARAM>"
HUGGING_FACE_API_TOKEN = "<YOUR_PARAM>"
HUGGING_FACE_API_URL = "<YOUR_PARAM>"

# Функция для генерации изображения
async def generate_image(text: str) -> Image.Image:
    headers = {'Authorization': f'Bearer {HUGGING_FACE_API_TOKEN}'}
    payload = {'inputs': text}
    response = requests.post(HUGGING_FACE_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        raise Exception(f"Ошибка при генерации изображения: {response.status_code} {response.text}")

# Обработка команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Отправь мне текст, и я создам изображение.')

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    try:
        image = await generate_image(user_text)
        bio = BytesIO()
        bio.name = 'image.png'
        image.save(bio, 'PNG')
        bio.seek(0)
        await update.message.reply_photo(photo=bio)
    except Exception as e:
        await update.message.reply_text(f'Произошла ошибка: {e}')

# Основная функция
def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
