import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Получение курсов через API
def get_exchange_rates(api_key):
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/UAH"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["result"] == "success":
            usd_rate = data["conversion_rates"]["USD"]
            eur_rate = data["conversion_rates"]["EUR"]
            return usd_rate, eur_rate
        else:
            print(f"Ошибка API: {data.get('error-type', 'Неизвестная ошибка')}")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return None, None

# Сохранение в файл
def save_rates_to_file(amount, usd_rate, eur_rate, selected_currency, result):
    with open("rates.txt", "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp} | {amount} UAH to {selected_currency}: {result}\n")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Эй, лузер! Я бот для конвертации твоих жалких гривен. Похер, пиши /convert и сумму, дебил (например, /convert 100).")

# Команда /convert
async def convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Извлекаем сумму из команды
        amount = float(update.message.text.split()[1])
        context.user_data['amount'] = amount  # Сохраняем сумму для следующего шага

        # Создаём кнопки для выбора валюты
        keyboard = [
            [InlineKeyboardButton("USD", callback_data="USD")],
            [InlineKeyboardButton("EUR", callback_data="EUR")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"Ты ввёл {amount} UAH, нищеброд. Куда конвертить твои копейки, дебил?", reply_markup=reply_markup)
    except (IndexError, ValueError):
        await update.message.reply_text("Ты что, тупой? Пиши сумму нормально, дебил, типа /convert 100!")

# Обработка выбора валюты
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Получаем сумму из сохранённых данных
    amount = context.user_data.get('amount')
    if not amount:
        await query.message.reply_text("Сумму не вижу, дебил! Пиши /convert заново, дебич!")
        return

    # Получаем курсы
    api_key = "YOUR_API_KEY"  # Заменил для безопасности
    usd_rate, eur_rate = get_exchange_rates(api_key)

    if usd_rate and eur_rate:
        selected_currency = query.data  # USD или EUR
        if selected_currency == "USD":
            rate = usd_rate
            result = amount * usd_rate
        else:  # EUR
            rate = eur_rate
            result = amount * eur_rate

        # Выводим результат
        await query.message.reply_text(f"Твои {amount} UAH это {result:.2f} {selected_currency}, нищеброд. Похер, радуйся!")
        save_rates_to_file(amount, usd_rate, eur_rate, selected_currency, result)
    else:
        await query.message.reply_text("Курсы не грузятся, дебил. Вали отсюда и пробуй позже!")

# Запуск бота
def main():
    bot_token = "YOUR_BOT_TOKEN"  # Заменил для безопасности
    app = Application.builder().token(bot_token).build()

    # Добавляем команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("convert", convert))
    app.add_handler(CallbackQueryHandler(button))

    # Запускаем бота
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
