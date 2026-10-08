import sqlite3

DB_NAME = "SchoolQuizDB.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Создаём таблицу Users
cursor.execute("""
CREATE TABLE IF NOT EXISTS Users (
    login TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

# Добавляем пользователей
cursor.execute("DELETE FROM Users")  # очищаем на всякий случай
cursor.execute("INSERT INTO Users (login, password, role) VALUES (?, ?, ?)", ('ученик', '123', 'student'))
cursor.execute("INSERT INTO Users (login, password, role) VALUES (?, ?, ?)", ('учитель', 'admin', 'teacher'))

conn.commit()

# Проверяем
cursor.execute("SELECT login, password, role FROM Users")
print("Таблица Users создана и заполнена:")
for row in cursor.fetchall():
    print(f"Логин: {row[0]}, Пароль: {row[1]}, Роль: {row[2]}")

conn.close()
print("\nГотово! Теперь запускай quiz_app.py")