import pyodbc
import telegram
import datetime
import pytz
from telegram.ext import Updater, CommandHandler


bot = telegram.Bot(token='6049300937:AAGnDwH5rLyr4NhQxisF9goiYpH0b-sTFlA')
local_tz = pytz.timezone('Europe/Chisinau')
connection = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};'
                            'SERVER=ENXYZT;'
                            'DATABASE=master;'
                            'TRUSTED_CONNECTION=yes;')

def start(update, context):
    reply_markup = {
        'keyboard': [['/now', '/next'], ['/today', '/tomorrow'], ['/week']],
        'one_time_keyboard': False,
        'resize_keyboard': True
    }
    bot.send_message(chat_id=update.effective_chat.id, text='Выберите действие:', reply_markup=reply_markup)


# функция для получения текущей пары
def get_current_subject():
    cursor = connection.cursor()
    query = "SELECT TOP 1 time_start, time_end, subject, subject_type, teacher, classroom  FROM schedule WHERE day = " \
            "? AND time_start <= ? AND time_end " \
            "> ? ORDER BY time_start "
    # получаем текущий день недели и текущее время
    current_day = datetime.datetime.now().strftime('%A').lower()
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    cursor.execute(query, (current_day, current_time, current_time))
    row = cursor.fetchone()
    # если найдена пара, возвращаем ее в формате строки
    if row:
        time_start = row[0].strftime("%H:%M")
        time_end = row[1].strftime("%H:%M")
        return f"❗{time_start} - {time_end}❗ {row[2]} | {row[3]} | {row[4]} | {row[5]}\n\n"
    else:
        # иначе проверяем, есть ли перемена, и сообщаем об этом
        query = "SELECT TOP 1 time_start FROM schedule WHERE day = ? AND time_start > ? ORDER BY time_start"
        cursor.execute(query, (current_day, current_time))
        row = cursor.fetchone()
        if row:
            time_until_next_subject = datetime.datetime.strptime(row[0].strftime('%H:%M:%S'), '%H:%M:%S') - datetime. \
                datetime.strptime(current_time, '%H:%M:%S')
            minutes_until_next_subject = int(time_until_next_subject.total_seconds() // 60)
            return f"Сейчас перемена, следующая пара через {minutes_until_next_subject} минут"
        else:
            return "Сегодня больше нет пар"


# функция для обработки команды /now
def handle_now(update, context):
    # получение текущей пары
    current_subject = get_current_subject()

    # отправка текущей пары пользователю
    bot.send_message(chat_id=update.effective_chat.id, text=current_subject)


def get_next_subject():
    cursor = connection.cursor()
    query = "SELECT TOP 1 time_start, time_end, subject, subject_type, teacher, classroom FROM schedule WHERE day = ? " \
            "AND time_start > ? ORDER BY time_start "
    current_day = datetime.datetime.now().strftime('%A').lower()
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    cursor.execute(query, (current_day, current_time))
    row = cursor.fetchone()
    if row:
        time_start = row[0].strftime("%H:%M")
        time_end = row[1].strftime("%H:%M")
        return f"❗{time_start} - {time_end}❗ {row[2]} | {row[3]} | {row[4]} | {row[5]}\n\n"
    else:
        return "Сегодня больше нет пар"


def handle_next(update, context):
    # получение текущей пары
    next_subject = get_next_subject()

    # отправка текущей пары пользователю
    bot.send_message(chat_id=update.effective_chat.id, text=next_subject)


# функция для получения пар на сегодня
def get_today_schedule():
    cursor = connection.cursor()
    query = "SELECT time_start, time_end, subject, subject_type, teacher, classroom, week_type FROM schedule WHERE day = ? ORDER " \
            "BY time_start "
    current_day = datetime.datetime.now().strftime('%A').lower()
    cursor.execute(query, (current_day,))
    rows = cursor.fetchall()
    # если пары на сегодня есть, формируем строку с ними
    if rows:
        schedule_string = "Расписание на сегодня:\n"
        for row in rows:
            time_start = row[0].strftime("%H:%M")
            time_end = row[1].strftime("%H:%M")
            schedule_string += f"❗{time_start} - {time_end}❗ {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]}\n\n"
        return schedule_string
    else:
        return "На сегодня пар нет"


# функция для обработки команды /today
def handle_today(update, context):
    # получение пар на сегодня
    today_schedule = get_today_schedule()

    # отправка пар пользователю
    bot.send_message(chat_id=update.effective_chat.id, text=today_schedule)


def get_tomorrow_schedule():
    cursor = connection.cursor()
    query = "SELECT time_start, time_end, subject, subject_type, teacher, classroom FROM schedule WHERE day = ? ORDER " \
            "BY time_start "
    tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%A').lower()
    cursor.execute(query, (tomorrow_str,))
    rows = cursor.fetchall()
    if rows:
        schedule_str = f"Расписание на {tomorrow.strftime('%d.%m.%Y')}:\n"
        for row in rows:
            time_start = row[0].strftime("%H:%M")
            time_end = row[1].strftime("%H:%M")
            schedule_str += f"❗{time_start} - {time_end}❗ {row[2]} | {row[3]} | {row[4]} | {row[5]}\n\n"
        return schedule_str
    else:
        return "Завтра нет пар"


def handle_tomorrow(update, context):
    # получение пар на сегодня
    tomorrow_schedule = get_tomorrow_schedule()

    # отправка пар пользователю
    bot.send_message(chat_id=update.effective_chat.id, text=tomorrow_schedule)


def get_week_schedule():
    cursor = connection.cursor()
    query = "SELECT day, time_start, time_end, subject, subject_type, teacher, classroom, week_type FROM schedule ORDER BY day, " \
            "time_start "
    cursor.execute(query)
    rows = cursor.fetchall()
    # если пары есть в БД
    if rows:
        schedule_string = "Расписание на всю неделю:\n"
        current_day = None
        for row in rows:
            # если сменился день недели, добавляем заголовок
            if row[0] != current_day:
                current_day = row[0]
                schedule_string += f"\n🗓️ {current_day.capitalize()}:\n"
            # формируем строку с информацией о паре
            time_start = row[1].strftime("%H:%M")
            time_end = row[2].strftime("%H:%M")
            schedule_string += f"❗{time_start} - {time_end} | {row[3]} | {row[4]} | {row[5]} | {row[6]} | {row[7]}\n\n"
        return schedule_string
    else:
        return "Нет расписания на всю неделю"


def handle_week(update, context):
    # получение пар на всю неделю
    week_schedule = get_week_schedule()

    # отправка пар пользователю
    bot.send_message(chat_id=update.effective_chat.id, text=week_schedule)



# запуск телеграм бота
updater = telegram.ext.Updater(token='6049300937:AAGnDwH5rLyr4NhQxisF9goiYpH0b-sTFlA', use_context=True)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('now', handle_now))
updater.dispatcher.add_handler(CommandHandler('next', handle_next))
updater.dispatcher.add_handler(CommandHandler('today', handle_today))
updater.dispatcher.add_handler(CommandHandler('tomorrow', handle_tomorrow))
updater.dispatcher.add_handler(CommandHandler('week', handle_week))
updater.start_polling()
updater.idle()

#

#
# cursor = connection.cursor()
# cursor.execute('Select * from schedule')
# for row in cursor:
#     print('row = %r' %(row,))


# #
# # функция для получения расписания на определенный день
# def get_schedule(day):
#     with connection.cursor() as cursor:
#         # выполнение запроса для получения расписания на определенный день
#         query = "SELECT * FROM schedule WHERE day=%s"
#         cursor.execute(query, (day,))
#         result = cursor.fetchall()
#
#         # форматирование полученного расписания в читаемый вид
#         schedule_text = ''
#         for item in result:
#             schedule_text += f'{item["time_start"]} - {item["time_end"]}: {item["subject"]}\n'
#
#         return schedule_text
#
# # функция для получения следующего предмета в зависимости от текущего времени
# def get_next_subject():
#     with connection.cursor() as cursor:
#         # выполнение запроса для получения следующего предмета
#         query = "SELECT * FROM schedule WHERE day=%s AND time_start > %s ORDER BY time_start LIMIT 1"
#         cursor.execute(query, (datetime.now().strftime('%A'), datetime.now().strftime('%H:%M')))
#         result = cursor.fetchone()
#
#         # форматирование полученного предмета в читаемый вид
#         next_subject = f'{result["time_start"]} - {result["time_end"]}: {result["subject"]}'
#         return next_subject
#
#
# # обработка команды для получения следующего предмета
# elif message_text.startswith('/next'):
#     # получение следующего предмета
#     next_subject = get_next_subject()
#
#     # отправка полученного предмета пользователю
#     bot.send_message(chat_id=update.effective_chat.id, text=next_subject)
#


# def get_schedule_for_day(day):
#     cursor = connection.cursor()
#     query = "SELECT time_start, time_end, subject, classroom FROM schedule WHERE day = ? ORDER BY time_start"
#     cursor.execute(query, day)
#     rows = cursor.fetchall()
#     schedule = ''
#     for row in rows:
#         schedule += f"{row[0]} - {row[1]} | {row[2]} | {row[3]}\n\n"
#     return schedule

# функция для обработки сообщений от пользователя
# def handle_message(update, context):
#     # получение текста сообщения от пользователя
#     message_text = update.message.text.lower()
#
#     # обработка команды для получения расписания на определенный день
#     if message_text.startswith('/schedule'):
#         try:
#             # получение дня из текста команды
#             day = message_text.split(' ')[1]
#
#             # получение расписания на указанный день
#             schedule = get_schedule_for_day(day)
#
#             # отправка полученного расписания пользователю
#             bot.send_message(chat_id=update.effective_chat.id, text=schedule)
#         except:
#             bot.send_message(chat_id=update.effective_chat.id,
#                              text="Ошибка в обработке команды. Введите корректную команду.")
#
#
# updater.dispatcher.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text, handle_message))
