from telegram.ext import Updater, CommandHandler
import handlers
import config
# Создание экземпляра Updater
updater = Updater(token=config.bot_token, use_context=True)

# Регистрация обработчиков команд
updater.dispatcher.add_handler(CommandHandler('start', handlers.start, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('now', handlers.handle_now, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('next', handlers.handle_next, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('today', handlers.handle_today, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('tomorrow', handlers.handle_tomorrow, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('week', handlers.handle_week, pass_args=True))


# Запуск бота
updater.start_polling()
updater.idle()
