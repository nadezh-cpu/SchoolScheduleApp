import customtkinter as ctk
from tkinter import ttk, messagebox
import pyodbc

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

CONN_STR = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost;"
    "Database=SchoolSchedule;"
    "Trusted_Connection=yes;"
)

def get_db_connection():
    return pyodbc.connect(CONN_STR)

class LoginApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("🏫 Школьное расписание - Вход")
        self.window.geometry("500x650")
        self.window.configure(fg_color="#f0f0f0")
        self.create_login_screen()
    
    def run(self):
        self.window.mainloop()
        
    def create_login_screen(self):
        for widget in self.window.winfo_children():
            widget.destroy()
        
        main_frame = ctk.CTkFrame(self.window, fg_color="white", corner_radius=20)
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        ctk.CTkLabel(main_frame, text="🏫 ШКОЛЬНОЕ РАСПИСАНИЕ", font=ctk.CTkFont(size=28, weight="bold"), text_color="#2c3e50").pack(pady=(40, 10))
        ctk.CTkLabel(main_frame, text="Войдите в систему", font=ctk.CTkFont(size=14), text_color="#7f8c8d").pack(pady=(0, 40))
        
        login_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        login_frame.pack(pady=10)
        ctk.CTkLabel(login_frame, text="📧 Логин", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        self.login_entry = ctk.CTkEntry(login_frame, width=350, height=45, font=ctk.CTkFont(size=14), corner_radius=10, placeholder_text="Введите ваш логин")
        self.login_entry.pack(pady=(5, 0))
        
        password_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        password_frame.pack(pady=15)
        ctk.CTkLabel(password_frame, text="🔒 Пароль", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        self.password_entry = ctk.CTkEntry(password_frame, width=350, height=45, font=ctk.CTkFont(size=14), corner_radius=10, show="•", placeholder_text="Введите пароль")
        self.password_entry.pack(pady=(5, 0))
        
        self.login_btn = ctk.CTkButton(main_frame, text="🔓 ВОЙТИ", command=self.login, width=350, height=50, font=ctk.CTkFont(size=16, weight="bold"), corner_radius=10, fg_color="#3498db", hover_color="#2980b9")
        self.login_btn.pack(pady=(30, 10))
        
        info_frame = ctk.CTkFrame(main_frame, fg_color="#ecf0f1", corner_radius=10)
        info_frame.pack(pady=20, padx=20, fill="x")
        ctk.CTkLabel(info_frame, text="📋 Тестовые аккаунты:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#2c3e50").pack(pady=(10, 5))
        ctk.CTkLabel(info_frame, text="ivanov / 12345 → 4 класс\npetrov / 12345 → 5 класс\nsidorov / 12345 → 6 класс\nsmirnov / 12345 → 7 класс\nkozlov / 12345 → 8 класс\nmorozov / 12345 → 9 класс\nvolkov / 12345 → 10 класс\nzaytsev / 12345 → 11 класс\nteacher / admin → учитель", font=ctk.CTkFont(size=11), text_color="#7f8c8d", justify="left").pack(pady=(0, 10))
        
    def login(self):
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not login or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль!")
            return
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT class_name, full_name, role FROM Users WHERE login = ? AND password = ?", (login, password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                self.window.destroy()
                ScheduleApp(user, login).run()
            else:
                messagebox.showerror("Ошибка", "Неверный логин или пароль!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка подключения: {e}")

class ScheduleApp:
    def __init__(self, user, login):
        self.user = user
        self.login = login
        self.class_name = user[0]
        self.full_name = user[1]
        self.role = user[2]
        
        self.window = ctk.CTk()
        self.window.title(f"🏫 Школьное расписание - {self.full_name}")
        self.window.geometry("1400x800")
        self.window.configure(fg_color="#f0f0f0")
        
        self.create_header()
        self.create_main_frame()
        self.create_table()
        self.create_footer()
        
        if self.class_name != '0':
            self.window.after(500, lambda: self.load_schedule(self.class_name))
        
    def run(self):
        self.window.mainloop()
        
    def create_header(self):
        header = ctk.CTkFrame(self.window, height=100, corner_radius=0, fg_color="#2c3e50")
        header.pack(fill="x")
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(header, text="🏫 РАСПИСАНИЕ УРОКОВ", font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
        title.pack(pady=(20, 5))
        
        info_frame = ctk.CTkFrame(header, fg_color="transparent")
        info_frame.pack()
        
        role_text = "УЧИТЕЛЬ" if self.role == 'teacher' else f"УЧЕНИК {self.class_name} КЛАССА"
        ctk.CTkLabel(info_frame, text=f"👤 {self.full_name} | {role_text}", font=ctk.CTkFont(size=12), text_color="#bdc3c7").pack(side="left", padx=10)
        
        if self.role == 'teacher':
            ctk.CTkLabel(info_frame, text="Выбрать класс:", font=ctk.CTkFont(size=12), text_color="white").pack(side="left", padx=10)
            self.class_combo = ctk.CTkComboBox(info_frame, values=['4','5','6','7','8','9','10','11'], width=80, height=30)
            self.class_combo.pack(side="left", padx=5)
            self.class_combo.set('4')
            
            self.show_btn = ctk.CTkButton(info_frame, text="📅 Показать", command=lambda: self.load_schedule(self.class_combo.get()), width=100, height=30, fg_color="#27ae60", hover_color="#2ecc71")
            self.show_btn.pack(side="left", padx=10)
        
        logout_btn = ctk.CTkButton(info_frame, text="🚪 Выход", command=self.logout, width=80, height=30, fg_color="#e74c3c", hover_color="#c0392b")
        logout_btn.pack(side="left", padx=20)
        
    def create_main_frame(self):
        self.main_frame = ctk.CTkFrame(self.window, corner_radius=10, fg_color="white")
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
    def create_table(self):
        self.tree_frame = ctk.CTkFrame(self.main_frame, fg_color="white")
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("num", "time", "mon", "tue", "wed", "thu", "fri")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=12, style="Custom.Treeview")
        
        style = ttk.Style()
        style.configure("Custom.Treeview", font=("Segoe UI", 11), rowheight=80, background="white", foreground="#333333")
        style.configure("Custom.Treeview.Heading", font=("Segoe UI", 12, "bold"), foreground="#2c3e50", background="#ecf0f1")
        
        self.tree.heading("num", text="№", anchor="center")
        self.tree.heading("time", text="⏰ Время", anchor="center")
        self.tree.heading("mon", text="ПН", anchor="center")
        self.tree.heading("tue", text="ВТ", anchor="center")
        self.tree.heading("wed", text="СР", anchor="center")
        self.tree.heading("thu", text="ЧТ", anchor="center")
        self.tree.heading("fri", text="ПТ", anchor="center")
        
        self.tree.column("num", width=60, anchor="center")
        self.tree.column("time", width=100, anchor="center")
        for col in ["mon", "tue", "wed", "thu", "fri"]:
            self.tree.column(col, width=220, anchor="w")
        
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        
        self.lesson_times = {
            1: "08:50\n09:30", 2: "09:50\n10:20", 3: "10:40\n11:20",
            4: "11:40\n12:20", 5: "12:30\n13:10", 6: "13:20\n14:00",
            7: "14:05\n14:45", 8: "14:50\n15:30"
        }
        
        for lesson_num in range(1, 9):
            self.tree.insert("", "end", values=(lesson_num, self.lesson_times[lesson_num], "", "", "", "", ""))
        
    def create_footer(self):
        footer = ctk.CTkFrame(self.window, height=35, corner_radius=0, fg_color="#2c3e50")
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        ctk.CTkLabel(footer, text="© Школьное расписание | Автоматизированная система", font=ctk.CTkFont(size=11), text_color="#bdc3c7").pack()
        
    def load_schedule(self, selected_class):
        # Очищаем таблицу
        for item in self.tree.get_children():
            lesson_num = self.tree.item(item, "values")[0]
            self.tree.item(item, values=(lesson_num, self.lesson_times[int(lesson_num)], "", "", "", "", ""))
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Дни недели: 1-ПН, 2-ВТ, 3-СР, 4-ЧТ, 5-ПТ
            for day in range(1, 6):
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
                """, (str(selected_class), day))
                
                rows = cursor.fetchall()
                
                for row in rows:
                    lesson_num = row[0]
                    teacher_name = f"{row[2]} {row[3][0]}.{row[4][0]}."
                    cell_text = f"📖 {row[1]}\n👩‍🏫 {teacher_name}\n🏫 Каб. {row[5]}"
                    
                    for item in self.tree.get_children():
                        values = list(self.tree.item(item, "values"))
                        if int(values[0]) == lesson_num:
                            # day+1 потому что колонки: 0-номер,1-время,2-ПН,3-ВТ,4-СР,5-ЧТ,6-ПТ
                            values[day+1] = cell_text
                            self.tree.item(item, values=values)
                            break
            
            conn.close()
            messagebox.showinfo("Успех", f"Расписание для {selected_class} класса загружено!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки: {e}")
    
    def logout(self):
        self.window.destroy()
        LoginApp().run()

if __name__ == "__main__":
    app = LoginApp()
    app.run()