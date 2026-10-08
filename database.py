import pyodbc
from db_config import CONN_STR

def get_connection():
    try:
        conn = pyodbc.connect(CONN_STR)
        print("✅ Подключено!")
        return conn
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def get_classes():
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute("SELECT class_name FROM Schedule GROUP BY class_name ORDER BY MIN(CAST(class_name AS INT))")
    classes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return classes

def get_schedule(class_name, weekday):
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            s.lesson_number,
            CAST(lt.start_time AS VARCHAR(5)),
            CAST(lt.end_time AS VARCHAR(5)),
            sub.subject_name,
            t.last_name + ' ' + LEFT(t.first_name, 1) + '.' + LEFT(t.patronymic, 1) + '.',
            c.room_number
        FROM Schedule s
        JOIN LessonTime lt ON s.lesson_number = lt.lesson_number
        JOIN Subjects sub ON s.subject_id = sub.id
        JOIN Teachers t ON s.teacher_id = t.id
        JOIN Classrooms c ON s.room_id = c.id
        WHERE s.class_name = ? AND s.weekday = ?
        ORDER BY s.lesson_number
    """, (class_name, weekday))
    rows = cursor.fetchall()
    conn.close()
    return rows

def test_connection():
    conn = get_connection()
    if conn:
        print("✅ База данных работает!")
        conn.close()
        return True
    return False