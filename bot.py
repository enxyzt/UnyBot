from telegram.ext import Updater, CommandHandler
import handlers
import config
# Creating an instance of Updater
updater = Updater(token=config.bot_token, use_context=True)

# Registering command handlers
updater.dispatcher.add_handler(CommandHandler('start', handlers.start, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('now', handlers.handle_now, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('next', handlers.handle_next, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('today', handlers.handle_today, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('tomorrow', handlers.handle_tomorrow, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('week', handlers.handle_week, pass_args=True))


# Launching the bot
updater.start_polling()
updater.idle()
#Bot created by Lungu Maxim