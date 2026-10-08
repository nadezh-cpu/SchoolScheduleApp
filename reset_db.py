import sqlite3

DB_NAME = "SchoolQuizDB.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Создаём таблицу
cursor.execute("""
CREATE TABLE Users (
    login TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

# Добавляем пользователей
cursor.execute("INSERT INTO Users (login, password, full_name, role) VALUES (?, ?, ?, ?)",
               ('ученик', '123', 'Иван Петров', 'student'))
cursor.execute("INSERT INTO Users (login, password, full_name, role) VALUES (?, ?, ?, ?)",
               ('учитель', 'admin', 'Анна Сидорова', 'teacher'))

conn.commit()
conn.close()

print("База данных SchoolQuizDB.db создана с таблицей Users")