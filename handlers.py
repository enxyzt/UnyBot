from schedule import get_current_subject, get_next_subject, get_today_schedule, get_tomorrow_schedule, get_week_schedule, save_chat_id, get_all_chat_ids
import telegram
import config
from apscheduler.schedulers.background import BackgroundScheduler


bot = telegram.Bot(token=config.bot_token)
scheduler = BackgroundScheduler()
# Установка часового пояса, например, 'Europe/Moscow'
scheduler.configure(timezone='Europe/Chisinau')

def send_daily_schedule():
    chat_ids = get_all_chat_ids()  # Получить все сохраненные chat_id из базы данных или файла

    for chat_id in chat_ids:
        schedule = get_today_schedule()
        bot.send_message(chat_id=chat_id, text=schedule)


# Запланировать выполнение функции send_daily_schedule каждый день в 7 утра
scheduler.add_job(send_daily_schedule, 'cron', hour=7, minute=30)

# Запустить планировщик
scheduler.start()

def start(update, context):
    chat_id = update.message.chat_id
    username = update.effective_chat.username
    save_chat_id(chat_id, username)
    reply_markup = {
        'keyboard': [['/now', '/next'], ['/today', '/tomorrow'], ['/week']],
        'one_time_keyboard': False,
        'resize_keyboard': True
    }
    bot.send_message(chat_id=update.effective_chat.id, text='Alegeți o acțiune:', reply_markup=reply_markup)


# Function for handling the /now command
def handle_now(update, context):
    # Getting the current subject
    current_subject = get_current_subject()

    # Sending the current subject to the user
    bot.send_message(chat_id=update.effective_chat.id, text=current_subject)


def handle_next(update, context):
    # Getting the next subject
    next_subject = get_next_subject()

    # Sending the next subject to the user
    bot.send_message(chat_id=update.effective_chat.id, text=next_subject)


# Function for handling the /today command
def handle_today(update, context):
    # Getting the subjects for today
    today_schedule = get_today_schedule()

    # Sending the subjects to the user
    bot.send_message(chat_id=update.effective_chat.id, text=today_schedule)


def handle_tomorrow(update, context):
    # получение пар на сегодня
    tomorrow_schedule = get_tomorrow_schedule()

    # отправка пар пользователю
    bot.send_message(chat_id=update.effective_chat.id, text=tomorrow_schedule)


def handle_week(update, context):
    # Getting the subjects for the entire week
    week_schedule = get_week_schedule()

    # Sending the subjects to the user
    bot.send_message(chat_id=update.effective_chat.id, text=week_schedule)
