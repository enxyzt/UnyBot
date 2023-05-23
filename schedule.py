import pyodbc
import datetime
import utils
import config


connection = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};'
                            f'SERVER={config.db_server};'
                            f'DATABASE={config.db_name};'
                            'TRUSTED_CONNECTION=yes;'
                            'ODBCConnectionPooling=True')


def save_chat_id(chat_id, username):
    cursor = connection.cursor()

    # Проверка существования таблицы
    cursor.execute("SELECT COUNT(*) FROM sys.tables WHERE name = 'chat_ids'")
    table_exists = cursor.fetchone()[0]

    # Создание таблицы chat_ids, если она не существует
    if not table_exists:
        cursor.execute("CREATE TABLE chat_ids (id INT PRIMARY KEY, username VARCHAR(255))")

    # Вставка данных chat_id и username в таблицу
    cursor.execute("INSERT INTO chat_ids (id, username) VALUES (?, ?)", (chat_id, username))

    # Подтверждение изменений в базе данных
    connection.commit()


def get_all_chat_ids():
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM chat_ids")
    rows = cursor.fetchall()
    chat_ids = [row[0] for row in rows]
    return chat_ids


# Function for getting the current subject
def get_current_subject():
    cursor = connection.cursor()
    query = "SELECT TOP 1 time_start, time_end, subject, subject_type, teacher, classroom  FROM schedule WHERE day = " \
            "? AND time_start <= ? AND time_end " \
            "> ? ORDER BY time_start "
    # Get the current day of the week and current time
    current_day = datetime.datetime.now().strftime('%A').lower()
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    cursor.execute(query, (current_day, current_time, current_time))
    row = cursor.fetchone()
    # If a subject is found, return it as a string
    if row:
        time_start = row[0].strftime("%H:%M")
        time_end = row[1].strftime("%H:%M")
        return f"❗{time_start} - {time_end}❗ {row[2]} | {row[3]} | {row[4]} | {row[5]}\n\n"
    else:
        # Otherwise, check for breaks and inform the user
        query = "SELECT TOP 1 time_start FROM schedule WHERE day = ? AND time_start > ? ORDER BY time_start"
        cursor.execute(query, (current_day, current_time))
        row = cursor.fetchone()
        if row:
            time_until_next_subject = datetime.datetime.strptime(row[0].strftime('%H:%M:%S'), '%H:%M:%S') - datetime. \
                datetime.strptime(current_time, '%H:%M:%S')
            minutes_until_next_subject = int(time_until_next_subject.total_seconds() // 60)
            return f"Acum este pauza, următoarea oră este peste {minutes_until_next_subject} minute."
        else:
            return "Astăzi nu mai avem ore."

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
        return "Astăzi nu mai avem ore."

# Function for getting the subjects for today
def get_today_schedule():
    cursor = connection.cursor()
    query = "SELECT time_start, time_end, subject, subject_type, teacher, classroom, week_type FROM schedule WHERE day = ? ORDER " \
            "BY time_start "
    current_day = datetime.datetime.now().strftime('%A').lower()
    cursor.execute(query, (current_day,))
    rows = cursor.fetchall()
    # If there are subjects for today, create a string with them
    if rows:
        schedule_string = "Orarul pentru astăzi:\n"
        current_week_type = utils.get_current_week_type()  # Function for determining the current week type

        for row in rows:
            # Check the week type for each subject
            week_type = row[6]
            if week_type is None or week_type == current_week_type:
                time_start = row[0].strftime("%H:%M")
                time_end = row[1].strftime("%H:%M")
                if week_type is None:
                    week_type = "Mereu"
                schedule_string += f"❗{time_start} - {time_end}❗ {row[2]} | {row[3]} | {row[4]} | {row[5]} | {week_type}\n\n"

        return schedule_string
    else:
        return "Astăzi nu mai avem ore."

def get_tomorrow_schedule():
    cursor = connection.cursor()
    query = "SELECT time_start, time_end, subject, subject_type, teacher, classroom, week_type FROM schedule WHERE day = ? ORDER " \
            "BY time_start "
    tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%A').lower()
    cursor.execute(query, (tomorrow_str,))
    rows = cursor.fetchall()
    # If there are subjects for today, create a string with them
    if rows:
        schedule_string = "Orarul pentru mâine:\n"
        current_week_type = utils.get_current_week_type()  #Function for determining the current week type

        for row in rows:
            # Check the week type for each subject
            week_type = row[6]
            if week_type is None or week_type == current_week_type:
                time_start = row[0].strftime("%H:%M")
                time_end = row[1].strftime("%H:%M")
                if week_type is None:
                    week_type = "Mereu"
                schedule_string += f"❗{time_start} - {time_end}❗ {row[2]} | {row[3]} | {row[4]} | {row[5]} | {week_type}\n\n"

        return schedule_string
    else:
        return "Mâine nu avem ore."

def get_week_schedule():
    cursor = connection.cursor()
    query = "SELECT day, time_start, time_end, subject, subject_type, teacher, classroom, week_type FROM schedule ORDER BY day, " \
            "time_start "
    cursor.execute(query)
    rows = cursor.fetchall()
    if rows:
        schedule_string = "Orarul pentru întreaga săptămână:\n"
        current_day = None
        for row in rows:
            # If the day of the week has changed, add a header
            if row[0] != current_day:
                current_day = row[0]
                schedule_string += f"\n🗓️ {current_day.capitalize()}:\n"
            # Create a string with information about the subject
            time_start = row[1].strftime("%H:%M")
            time_end = row[2].strftime("%H:%M")
            if row[7] is None:
               row[7] = "Mereu"
            schedule_string += f"❗{time_start} - {time_end} | {row[3]} | {row[4]} | {row[5]} | {row[6]} | {row[7]}\n\n"
        return schedule_string
    else:
        return "Nu există orar pentru întreaga săptămână."

