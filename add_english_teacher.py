import sqlite3

DB_NAME = "SchoolQuizDB.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Добавляем учителя с английским логином (если ещё нет)
cursor.execute("INSERT OR IGNORE INTO Users (login, password, role) VALUES (?, ?, ?)", 
               ('teacher', 'admin', 'teacher'))

conn.commit()

# Проверяем, что получилось
cursor.execute("SELECT login, password, role FROM Users")
print("Текущие пользователи в базе данных:")
for row in cursor.fetchall():
    print(f"Логин: '{row[0]}', Пароль: '{row[1]}', Роль: '{row[2]}'")

conn.close()
print("\nГотово! Теперь попробуй войти с логином 'teacher' и паролем 'admin'")
# Скрипт добавления учителя английского языка
# Ветка: second