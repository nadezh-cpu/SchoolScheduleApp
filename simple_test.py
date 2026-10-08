import pyodbc

CONN_STR = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost;"
    "Database=SchoolSchedule;"
    "Trusted_Connection=yes;"
)

try:
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    
    # Простой подсчёт
    cursor.execute("SELECT COUNT(*) FROM Schedule WHERE class_name = '8' AND weekday = 1")
    count = cursor.fetchone()[0]
    print(f"Всего записей для 8 класса в ПН: {count}")
    
    # Выбираем все поля
    cursor.execute("""
        SELECT 
            s.lesson_number, 
            sub.subject_name,
            t.last_name,
            t.first_name,
            t.patronymic,
            c.room_number
        FROM Schedule s
        LEFT JOIN Subjects sub ON s.subject_id = sub.id
        LEFT JOIN Teachers t ON s.teacher_id = t.id
        LEFT JOIN Classrooms c ON s.room_id = c.id
        WHERE s.class_name = '8' AND s.weekday = 1
        ORDER BY s.lesson_number
    """)
    
    rows = cursor.fetchall()
    print(f"Всего строк (без DISTINCT): {len(rows)}")
    
    for row in rows:
        print(row)
    
    conn.close()
    
except Exception as e:
    print(f"Ошибка: {e}")