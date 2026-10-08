import customtkinter as ctk
from tkinter import ttk
import pyodbc

CONN_STR = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost;"
    "Database=SchoolSchedule;"
    "Trusted_Connection=yes;"
)

def get_schedule(class_name, weekday):
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            s.lesson_number, 
            sub.subject_name,
            t.last_name,
            t.first_name,
            t.patronymic,
            c.room_number
        FROM Schedule s
        JOIN Subjects sub ON s.subject_id = sub.id
        JOIN Teachers t ON s.teacher_id = t.id
        JOIN Classrooms c ON s.room_id = c.id
        WHERE s.class_name = ? AND s.weekday = ?
        ORDER BY s.lesson_number
    """, (str(class_name), weekday))
    rows = cursor.fetchall()
    conn.close()
    return rows

class TestApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Тест расписания")
        self.window.geometry("1200x700")
        
        # Выбор класса
        frame = ctk.CTkFrame(self.window)
        frame.pack(pady=10)
        
        ctk.CTkLabel(frame, text="Класс:").pack(side="left", padx=5)
        self.class_combo = ctk.CTkComboBox(frame, values=['4','5','6','7','8','9','10','11'], width=80)
        self.class_combo.pack(side="left", padx=5)
        self.class_combo.set('8')
        
        ctk.CTkLabel(frame, text="День:").pack(side="left", padx=5)
        self.day_combo = ctk.CTkComboBox(frame, values=['ПН','ВТ','СР','ЧТ','ПТ'], width=80)
        self.day_combo.pack(side="left", padx=5)
        self.day_combo.set('ПН')
        
        btn = ctk.CTkButton(frame, text="Показать", command=self.show_schedule)
        btn.pack(side="left", padx=20)
        
        # Таблица
        self.tree_frame = ctk.CTkFrame(self.window)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("num", "subject", "teacher", "room")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("num", text="Урок")
        self.tree.heading("subject", text="Предмет")
        self.tree.heading("teacher", text="Учитель")
        self.tree.heading("room", text="Кабинет")
        
        self.tree.column("num", width=60, anchor="center")
        self.tree.column("subject", width=250)
        self.tree.column("teacher", width=250)
        self.tree.column("room", width=100, anchor="center")
        
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        
    def show_schedule(self):
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        class_name = self.class_combo.get()
        day_names = {'ПН':1, 'ВТ':2, 'СР':3, 'ЧТ':4, 'ПТ':5}
        weekday = day_names[self.day_combo.get()]
        
        rows = get_schedule(class_name, weekday)
        
        for row in rows:
            lesson_num = row[0]
            subject = row[1]
            teacher_name = f"{row[2]} {row[3][0]}.{row[4][0]}."
            room = row[5]
            self.tree.insert("", "end", values=(lesson_num, subject, teacher_name, room))
        
        if len(rows) == 0:
            self.tree.insert("", "end", values=("", "НЕТ ДАННЫХ", "", ""))
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = TestApp()
    app.run()