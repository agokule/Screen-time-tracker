from .get_process import get_active_window_app_name, get_active_window_app_path, get_app_name_from_exe, get_idle_time
import time
from datetime import datetime
from constants import DATE_FMT_SQL, TABLE_NAME, APP_EXE_COL, APP_NAME_COL, MAX_IDLE_TIME
import sqlite3

def flush_database(cursor: sqlite3.Cursor):
    cursor.connection.commit()


def add_program(cursor: sqlite3.Cursor, name: str, exe: str):
    cursor.execute(f"""
INSERT INTO {TABLE_NAME} ({APP_NAME_COL}, {APP_EXE_COL}, {datetime.now().strftime(DATE_FMT_SQL)})
VALUES (?,?,?)
""", (name, exe, 1))
    return cursor.lastrowid


def program_exists(cursor: sqlite3.Cursor, name: str, exe: str):
    cursor.execute(f"""
SELECT count(*)
FROM {TABLE_NAME}
WHERE (({APP_NAME_COL} = ?) AND ({APP_EXE_COL} = ?))
""", (name, exe))
    data = cursor.fetchone()
    return data[0] != 0


def increment_program(cursor: sqlite3.Cursor, name: str, exe: str):
    column = datetime.now().strftime(DATE_FMT_SQL)
    cursor.execute(f"""
UPDATE {TABLE_NAME}
SET {column} = {column} + 1
WHERE ({APP_NAME_COL} = ?) AND ({APP_EXE_COL} = ?)
""", (name, exe))


def write_data(cursor: sqlite3.Cursor, proc_name: str | None, app_name: str | None):
    if proc_name is None or app_name == '':
        return
    if app_name is None:
        app_name = str(app_name)
    try:
        cursor.execute("ALTER TABLE " + TABLE_NAME + " ADD COLUMN " + \
                    datetime.now().strftime(DATE_FMT_SQL) + \
                    " INTEGER default 0")
    except sqlite3.OperationalError as e:
        print(e)

    if not program_exists(cursor, app_name, proc_name):
        print("New program added", app_name)
        add_program(cursor, app_name, proc_name)
        return
    
    increment_program(cursor, app_name, proc_name)


def track(cursor: sqlite3.Cursor):
    filename, fullpath = get_active_window_app_name(), get_active_window_app_path()
    name = get_app_name_from_exe(fullpath)
    idle_time = get_idle_time()
    if idle_time <= MAX_IDLE_TIME:
        write_data(cursor, filename, name)
    return name, filename, idle_time


def main():
    while True:
        time.sleep(1)
        print(track())


if __name__ == '__main__':
    main()
