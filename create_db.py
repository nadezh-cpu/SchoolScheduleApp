import sqlite3
import os

DB_NAME = "SchoolQuizDB.db"

# Удаляем старый файл, если есть
if os.path.exists(DB_NAME):
    os.remove(DB_NAME)
    print(f"Старый файл {DB_NAME} удалён")

# Создаём новую базу данных
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Создаём таблицу Users с правильными колонками
cursor.execute("""
CREATE TABLE Users (
    login TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

# Добавляем тестовых пользователей
cursor.execute("INSERT INTO Users (login, password, full_name, role) VALUES (?, ?, ?, ?)",
               ('ученик', '123', 'Иван Петров', 'student'))
cursor.execute("INSERT INTO Users (login, password, full_name, role) VALUES (?, ?, ?, ?)",
               ('учитель', 'admin', 'Анна Сидорова', 'teacher'))

conn.commit()

# Проверяем
cursor.execute("SELECT * FROM Users")
print("Таблица Users создана и заполнена:")
for row in cursor.fetchall():
    print(f"Логин: {row[0]}, Пароль: {row[1]}, Имя: {row[2]}, Роль: {row[3]}")

conn.close()
print("\nГотово! Теперь запускай quiz_app.py")