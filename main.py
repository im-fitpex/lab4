import telebot
import requests
from telebot import types
import random

API_TOKEN = '8007301405:AAG6R3UwSHryQCq9bDS9JHlsU4yOhWh9A3o'
bot = telebot.TeleBot(API_TOKEN)

# URL для получения данных о книгах
BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes?q="

# Функция для поиска книги
def get_book_info(query):
    try:
        response = requests.get(BOOKS_API_URL + query)
        data = response.json()

        if 'items' in data:
            book_info = data['items'][0]['volumeInfo']
            title = book_info.get('title', 'Неизвестно')
            authors = ", ".join(book_info.get('authors', ['Неизвестно']))
            description = book_info.get('description', 'Описание отсутствует')
            rating = book_info.get('averageRating', 'Нет рейтинга')

            # Формируем основной блок информации
            result = f"📚 *Название:* {title}\n🎩 *Автор(ы):* {authors}\n⭐ *Рейтинг:* {rating}\n\n"
            
            # Проверка длины описания и разбивка на части
            if len(description) > 4096:
                description_parts = [description[i:i+4096] for i in range(0, len(description), 4096)]
                return result, description_parts
            else:
                return result + f"*Описание:*\n{description}", None
        else:
            return "Книга не найдена.", None
    except Exception as e:
        return f"Ошибка при получении данных: {e}", None

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Поиск книги'), 
               types.KeyboardButton('Случайная книга'),
               types.KeyboardButton('Справка'))
    markup.add(types.KeyboardButton('Топ книг'),
               types.KeyboardButton('Топ за месяц'),
               types.KeyboardButton('Топ за год'))
    bot.send_message(message.chat.id, 
                     "Привет! Я бот для поиска информации о книгах. Выберите одну из команд:",
                     reply_markup=markup)

# Команда /help
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id,
                     "Вот доступные команды:\n"
                     "/search - Найти книгу по названию.\n"
                     "/top - Показать топ книг.\n"
                     "/quit - Завершить работу с ботом.\n")

# Команда /search
@bot.message_handler(commands=['search'])
def search_book(message):
    msg = bot.send_message(message.chat.id, "Введите название книги для поиска:")
    bot.register_next_step_handler(msg, process_search)

# Обработка ввода текста для поиска книги
def process_search(message):
    query = message.text.strip()
    bot.send_chat_action(message.chat.id, 'typing')  # Имитируем печатание
    info, extra_parts = get_book_info(query)

    if extra_parts:
        bot.send_message(message.chat.id, info, parse_mode="Markdown")
        for part in extra_parts:
            bot.send_message(message.chat.id, part)
    else:
        bot.send_message(message.chat.id, info, parse_mode="Markdown")

# Команда /quit
@bot.message_handler(commands=['quit'])
def quit_bot(message):
    bot.send_message(message.chat.id, "До свидания! Ожидайте новых обновлений.")

# Кнопка "Поиск книги"
@bot.message_handler(func=lambda message: message.text == "Поиск книги")
def button_search(message):
    msg = bot.send_message(message.chat.id, "Введите название книги для поиска:")
    bot.register_next_step_handler(msg, process_search)

# Кнопка "Случайная книга"
@bot.message_handler(func=lambda message: message.text == "Случайная книга")
def random_book(message):
    popular_queries = ['Harry Potter', 'Sherlock Holmes', '1984', 'Pride and Prejudice', 'Dune']
    query = random.choice(popular_queries)
    bot.send_message(message.chat.id, "Ищу случайную книгу... 🎲")
    info, extra_parts = get_book_info(query)

    if extra_parts:
        bot.send_message(message.chat.id, info, parse_mode="Markdown")
        for part in extra_parts:
            bot.send_message(message.chat.id, part)
    else:
        bot.send_message(message.chat.id, info, parse_mode="Markdown")

# Кнопка "Топ книг"
@bot.message_handler(func=lambda message: message.text == "Топ книг")
def top_books(message):
    top_books_list = [
        'Atomic Habits - James Clear',
        'The Midnight Library - Matt Haig',
        'Where the Crawdads Sing - Delia Owens',
        'The Alchemist - Paulo Coelho',
        'Becoming - Michelle Obama'
    ]
    top_books_message = '\n'.join([f"💼 {book}" for book in top_books_list])
    bot.send_message(message.chat.id, f"Топ книг по популярности:\n{top_books_message}")

# Кнопка "Топ за месяц"
@bot.message_handler(func=lambda message: message.text == "Топ за месяц")
def top_month(message):
    books = [
        'Lessons in Chemistry - Bonnie Garmus',
        'The Paris Library - Janet Skeslien Charles',
        'Tomorrow, and Tomorrow, and Tomorrow - Gabrielle Zevin'
    ]
    message_text = '\n'.join([f"💼 {book}" for book in books])
    bot.send_message(message.chat.id, f"Топ книг за месяц:\n{message_text}")

# Кнопка "Топ за год"
@bot.message_handler(func=lambda message: message.text == "Топ за год")
def top_year(message):
    books = [
        'Project Hail Mary - Andy Weir',
        'The Four Winds - Kristin Hannah',
        'Klara and the Sun - Kazuo Ishiguro'
    ]
    message_text = '\n'.join([f"💼 {book}" for book in books])
    bot.send_message(message.chat.id, f"Топ книг за год:\n{message_text}")

# Кнопка "Справка"
@bot.message_handler(func=lambda message: message.text == "Справка")
def button_help(message):
    send_help(message)

# Запуск бота
if __name__ == "__main__":
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка: {e}")
