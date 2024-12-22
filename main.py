import logging
import random

import game
import requests
import json

from numpy import number
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import openai

# Настройка логирования
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Токены и API ключи
BOT_TOKEN = '8046195893:AAEfNDOtX4NYFaPqnF_oEqJ8YXjUQYHg1pA'
OMDB_API_KEY = 'http://www.omdbapi.com/?i=tt3896198&apikey=1e3f1394'
TRANSLATION_API_URL = "https://api.mymemory.translated.net/get"
DOG_API_URL = "https://dog.ceo/api/breeds/image/random"
CAT_API_URL = "https://api.thecatapi.com/v1/images/search"
ADVICE_API_URL = "https://api.adviceslip.com/advice"
FACT_API_URL = "https://uselessfacts.jsph.pl/random.json?language=en"
MUSIC_API_URL = "https://api.deezer.com/chart"
OPENAI_API_KEY = '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'
UNSPLASH_API_KEY = '5qrxk0cVaix-mnYTr_auuvGumzWp2eBQlp5_ZnPAXLE'  # Ваш API ключ для Unsplash
UNSPLASH_API_URL = 'https://api.unsplash.com/photos/random'  # Для поиска изображений
NEWS_API_KEY = 'af446556a648456b999fe37f01943068'  # API для новостей
QUOTABLE_API_URL = "https://api.quotable.io/random"

# Основная функция для запуска бота
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "🔥 Привет! Я твой многофункциональный бот! Вот что я умею:\n\n"
        "1. /weather [город] - Погода\n"
        "2. /fact - Случайный факт\n"
        "3. /movie [название] - Поиск фильмов\n"
        "4. /random - Случайное число\n"
        "5. /game - Угадай число\n"
        "6. /quote - Случайная цитата\n"
        "7. /joke - Шутка\n"
        "8. /advice - Полезный совет\n"
        "9. /dog - Фото собаки\n"
        "10. /cat - Фото кота\n"
        "11. /translate [текст] - Перевод текста\n"
        "12. /music - Популярные треки\n"
        "13. /chatgpt [вопрос] - Общение с ChatGPT\n"
        "14. /support - Поддержка, если тебе плохо\n"
        "15. /cyberpunk - Киберпанк фото ночью\n"
        "16. /news - Получить новости\n"
        "17. /image - Случайное изображение"
    )

# Погода
async def weather(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        await update.message.reply_text("Укажите город для поиска погоды, например: /weather Москва")
        return

    city = " ".join(context.args)
    try:
        # Получаем текстовый ответ
        response = requests.get(f"https://wttr.in/{city}?format=🌀 %C\n🌡 %t\n🌬 Ветер: %w\n💧 Влажность: %h")
        if response.status_code == 200:
            weather_data = response.text
            await update.message.reply_text(f"Погода в {city}:\n{weather_data}")
        else:
            await update.message.reply_text(
                "Не удалось получить данные о погоде. Убедитесь, что вы указали правильное название города.")
    except Exception as e:
        logging.error(f"Ошибка при получении погоды: {e}")
        await update.message.reply_text("Произошла ошибка при запросе погоды. Попробуйте позже.")

# Случайные факты
async def fact(update: Update, context: CallbackContext) -> None:
    try:
        response = requests.get(FACT_API_URL)
        fact_data = response.json()
        fact_message = fact_data['text']
        await update.message.reply_text(fact_message)
    except Exception as e:
        logging.error(f"Ошибка при получении факта: {e}")
        await update.message.reply_text("Не удалось получить факт.")

# Поиск фильма
async def movie(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        await update.message.reply_text("Укажите название фильма для поиска, например: /movie Inception")
        return
    movie_name = " ".join(context.args)
    try:
        response = requests.get(f"http://www.omdbapi.com/?t={movie_name}&apikey={OMDB_API_KEY}")
        movie_data = response.json()
        if movie_data.get("Response") == "False":
            await update.message.reply_text("Фильм не найден!")
        else:
            title = movie_data["Title"]
            year = movie_data["Year"]
            plot = movie_data["Plot"]
            poster = movie_data["Poster"]
            movie_message = f"Фильм: {title}\nГод: {year}\nОписание: {plot}"
            await update.message.reply_text(movie_message)
            await update.message.reply_photo(poster)
    except Exception as e:
        logging.error(f"Ошибка при получении информации о фильме: {e}")
        await update.message.reply_text("Не удалось получить данные о фильме.")

# Случайное число
async def random_number(update: Update, context: CallbackContext) -> None:
    random_num = random.randint(1, 100)
    await update.message.reply_text(f"Случайное число: {random_num}")

# Начало игры
async def game(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "🎮 Давайте сыграем в 'Камень, ножницы, бумага'! Напишите один из вариантов: камень, ножницы или бумага."
    )
    context.user_data["game_active"] = True

# Проверка выбора игрока
async def check_rps(update: Update, context: CallbackContext) -> None:
    if not context.user_data.get("game_active"):
        await update.message.reply_text("Для начала игры введите команду /rps.")
        return

    user_choice = update.message.text.lower()
    valid_choices = ["камень", "ножницы", "бумага"]
    if user_choice not in valid_choices:
        await update.message.reply_text("⛔ Пожалуйста, выберите только: камень, ножницы или бумага.")
        return

    bot_choice = random.choice(valid_choices)
    await update.message.reply_text(f"🤖 Мой выбор: {bot_choice.capitalize()}")

    # Определяем результат игры
    if user_choice == bot_choice:
        await update.message.reply_text("⚖️ Ничья!")
    elif (
        (user_choice == "камень" and bot_choice == "ножницы") or
        (user_choice == "ножницы" and bot_choice == "бумага") or
        (user_choice == "бумага" and bot_choice == "камень")
    ):
        await update.message.reply_text("🎉 Вы выиграли!")
    else:
        await update.message.reply_text("😢 Я выиграл!")

    # Завершаем игру
    context.user_data["game_active"] = False
    await update.message.reply_text("Для новой игры введите команду /game.")


# Цитаты через API
async def quote(update: Update, context: CallbackContext) -> None:
    try:
        response = requests.get(QUOTABLE_API_URL)
        quote_data = response.json()
        quote_message = f"Цитата: \n{quote_data['content']}\n— {quote_data['author']}"
        await update.message.reply_text(quote_message)
    except Exception as e:
        logging.error(f"Ошибка при получении цитаты: {e}")
        await update.message.reply_text("Не удалось получить цитату.")

# Шутка
async def joke(update: Update, context: CallbackContext) -> None:
    try:
        response = requests.get("https://official-joke-api.appspot.com/jokes/random")
        joke_data = response.json()
        joke_message = f"{joke_data['setup']} - {joke_data['punchline']}"
        await update.message.reply_text(joke_message)
    except Exception as e:
        logging.error(f"Ошибка при получении шутки: {e}")
        await update.message.reply_text("Не удалось получить шутку.")

# Советы через API
async def advice(update: Update, context: CallbackContext) -> None:
    try:
        response = requests.get(ADVICE_API_URL)
        advice_data = response.json()
        advice_message = advice_data['slip']['advice']
        await update.message.reply_text(f"Полезный совет: {advice_message}")
    except Exception as e:
        logging.error(f"Ошибка при получении совета: {e}")
        await update.message.reply_text("Не удалось получить совет.")

# Фото собаки
async def dog(update: Update, context: CallbackContext) -> None:
    try:
        response = requests.get(DOG_API_URL)
        dog_data = response.json()
        dog_image_url = dog_data['message']
        await update.message.reply_photo(dog_image_url)
    except Exception as e:
        logging.error(f"Ошибка при получении фото собаки: {e}")
        await update.message.reply_text("Не удалось получить фото собаки.")

# Фото кота
async def cat(update: Update, context: CallbackContext) -> None:
    try:
        response = requests.get(CAT_API_URL)
        cat_data = response.json()
        cat_image_url = cat_data[0]['url']
        await update.message.reply_photo(cat_image_url)
    except Exception as e:
        logging.error(f"Ошибка при получении фото кота: {e}")
        await update.message.reply_text("Не удалось получить фото кота.")

# Перевод текста
async def translate(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        await update.message.reply_text("Укажите текст для перевода, например: /translate Привет")
        return
    text_to_translate = " ".join(context.args)
    try:
        response = requests.get(f"{TRANSLATION_API_URL}?q={text_to_translate}&langpair=ru|en")
        translation_data = response.json()
        translated_text = translation_data['responseData']['translatedText']
        await update.message.reply_text(f"Перевод: {translated_text}")
    except Exception as e:
        logging.error(f"Ошибка при переводе: {e}")
        await update.message.reply_text("Не удалось перевести текст.")

# Музыка
async def music(update: Update, context: CallbackContext) -> None:
    try:
        response = requests.get(MUSIC_API_URL)
        music_data = response.json()
        music_message = "\n".join([f"{track['title']} - {track['artist']['name']}" for track in music_data['data'][:5]])
        await update.message.reply_text(f"Популярные треки:\n{music_message}")
    except Exception as e:
        logging.error(f"Ошибка при получении музыки: {e}")
        await update.message.reply_text("Не удалось получить информацию о музыке.")

# ChatGPT
async def chatgpt(update: Update, context: CallbackContext) -> None:
    question = " ".join(context.args)
    try:
        openai.api_key = OPENAI_API_KEY
        response = openai.Completion.create(
            model="gpt-3.5-turbo",
            prompt=question,
            max_tokens=150
        )
        chatgpt_response = response.choices[0].text.strip()
        await update.message.reply_text(chatgpt_response)
    except Exception as e:
        logging.error(f"Ошибка при общении с ChatGPT: {e}")
        await update.message.reply_text("Не удалось получить ответ от ChatGPT.")

# Поддержка
async def support(update: Update, context: CallbackContext) -> None:
    try:
        response = requests.get(ADVICE_API_URL)
        advice_data = response.json()
        advice_message = advice_data['slip']['advice']
        await update.message.reply_text(f"Полезный совет для поддержки: {advice_message}")
    except Exception as e:
        logging.error(f"Ошибка при получении совета поддержки: {e}")
        await update.message.reply_text("Не удалось получить совет поддержки.")

# Новости
async def news(update: Update, context: CallbackContext) -> None:
    try:
        response = requests.get(f'https://newsapi.org/v2/top-headlines?country=ru&apiKey={NEWS_API_KEY}')
        news_data = response.json()
        articles = news_data['articles'][:5]
        news_message = "\n".join([f"{article['title']} - {article['url']}" for article in articles])
        await update.message.reply_text(f"Новости:\n{news_message}")
    except Exception as e:
        logging.error(f"Ошибка при получении новостей: {e}")
        await update.message.reply_text("Не удалось получить новости.")

# Случайное изображение
async def image(update: Update, context: CallbackContext) -> None:
    try:
        response = requests.get(f'{UNSPLASH_API_URL}?client_id={UNSPLASH_API_KEY}')
        image_data = response.json()
        image_url = image_data[0]['urls']['regular']
        await update.message.reply_photo(image_url)
    except Exception as e:
        logging.error(f"Ошибка при получении изображения: {e}")
        await update.message.reply_text("Не удалось получить изображение.")

# Основная функция
def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("weather", weather))
    application.add_handler(CommandHandler("fact", fact))
    application.add_handler(CommandHandler("movie", movie))
    application.add_handler(CommandHandler("random", random_number))
    application.add_handler(CommandHandler("game", game))
    application.add_handler(CommandHandler("quote", quote))
    application.add_handler(CommandHandler("joke", joke))
    application.add_handler(CommandHandler("advice", advice))
    application.add_handler(CommandHandler("dog", dog))
    application.add_handler(CommandHandler("cat", cat))
    application.add_handler(CommandHandler("translate", translate))
    application.add_handler(CommandHandler("music", music))
    application.add_handler(CommandHandler("chatgpt", chatgpt))
    application.add_handler(CommandHandler("support", support))
    application.add_handler(CommandHandler("news", news))
    application.add_handler(CommandHandler("image", image))

    application.run_polling()

if __name__ == "__main__":
    main()
