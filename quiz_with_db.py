import customtkinter as ctk
from tkinter import messagebox
import random
import pyodbc

# =============================================
# НАСТРОЙКА ЦВЕТОВОЙ ТЕМЫ
# =============================================
COLORS = {
    "primary": "#20B2AA",
    "secondary": "#66CDAA",
    "accent": "#8FBC8F",
    "bg": "#F0F8F0",
    "card": "#FFFFFF",
    "text_dark": "#2C3E50",
    "text_light": "#FFFFFF",
    "success": "#27AE60",
    "error": "#E74C3C",
    "hover": "#1A8A82"
}

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

# =============================================
# ПОДКЛЮЧЕНИЕ К БАЗЕ ДАННЫХ SQL SERVER
# =============================================

CONN_STR = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost;"
    "Database=QuizDB;"
    "Trusted_Connection=yes;"
)

def get_questions_from_db():
    """Загрузка вопросов из базы данных SQL Server"""
    try:
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        
        # Получаем все предметы и вопросы
        cursor.execute("""
            SELECT s.name, q.question_text, q.option1, q.option2, q.option3, q.option4, q.correct_answer
            FROM Questions q
            JOIN Subjects s ON q.subject_id = s.id
            ORDER BY s.name, q.id
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        # Преобразуем в словарь
        questions_db = {}
        for row in rows:
            subject = row[0]
            if subject not in questions_db:
                questions_db[subject] = []
            questions_db[subject].append({
                "question": row[1],
                "options": [row[2], row[3], row[4], row[5]],
                "correct": row[6] - 1  # в БД 1-4, в коде 0-3
            })
        
        return questions_db
        
    except Exception as e:
        messagebox.showerror("Ошибка БД", f"Не удалось подключиться к базе данных:\n{e}")
        return None

# Загружаем вопросы из БД
QUESTIONS_DB = get_questions_from_db()

class QuizApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("🎓 КВИЗ - 5 класс")
        self.window.geometry("1000x750")
        self.window.configure(fg_color=COLORS["bg"])
        
        self.player_name = ""
        self.selected_subject = ""
        self.current_question = 0
        self.score = 0
        self.user_answers = []
        self.questions = []
        self.user_choices = []
        
        self.create_name_screen()
    
    def run(self):
        self.window.mainloop()
    
    def clear_window(self):
        for widget in self.window.winfo_children():
            widget.destroy()
    
    def create_name_screen(self):
        self.clear_window()
        
        main_frame = ctk.CTkFrame(self.window, fg_color=COLORS["card"], corner_radius=20)
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        title_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["primary"], corner_radius=15, height=80)
        title_frame.pack(fill="x", padx=30, pady=(30, 20))
        title_frame.pack_propagate(False)
        
        ctk.CTkLabel(title_frame, text="🎓 КВИЗ ДЛЯ 5 КЛАССА", font=ctk.CTkFont(size=28, weight="bold"), text_color=COLORS["text_light"]).pack(expand=True)
        
        ctk.CTkLabel(main_frame, text="Проверь свои знания!", font=ctk.CTkFont(size=16), text_color=COLORS["primary"]).pack(pady=(0, 30))
        
        name_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        name_frame.pack(pady=20)
        
        ctk.CTkLabel(name_frame, text="📝 Введите ваше имя и фамилию:", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_dark"]).pack(anchor="w")
        self.name_entry = ctk.CTkEntry(name_frame, width=350, height=45, font=ctk.CTkFont(size=14), corner_radius=10, border_color=COLORS["secondary"], border_width=2, placeholder_text="Например: Иван Петров")
        self.name_entry.pack(pady=(5, 0))
        
        self.continue_btn = ctk.CTkButton(main_frame, text="➡️ ПРОДОЛЖИТЬ", command=self.save_name_and_go_to_subjects, width=300, height=50, font=ctk.CTkFont(size=16, weight="bold"), corner_radius=25, fg_color=COLORS["primary"], hover_color=COLORS["hover"])
        self.continue_btn.pack(pady=(40, 20))
        
        line = ctk.CTkFrame(main_frame, height=2, fg_color=COLORS["secondary"], corner_radius=1)
        line.pack(fill="x", padx=50, pady=20)
        
        ctk.CTkLabel(main_frame, text="5 предметов | 10 вопросов | Подсчёт баллов", font=ctk.CTkFont(size=12), text_color=COLORS["accent"]).pack()
    
    def save_name_and_go_to_subjects(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Ошибка", "Введите ваше имя и фамилию!")
            return
        self.player_name = name
        self.create_subject_screen()
    
    def create_subject_screen(self):
        self.clear_window()
        
        main_frame = ctk.CTkFrame(self.window, fg_color=COLORS["card"], corner_radius=20)
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        title_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["secondary"], corner_radius=15, height=70)
        title_frame.pack(fill="x", padx=30, pady=(30, 20))
        title_frame.pack_propagate(False)
        
        ctk.CTkLabel(title_frame, text=f"👋 Привет, {self.player_name}!", font=ctk.CTkFont(size=22, weight="bold"), text_color=COLORS["text_light"]).pack(expand=True)
        
        ctk.CTkLabel(main_frame, text="Выбери предмет для квиза:", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLORS["text_dark"]).pack(pady=(10, 25))
        
        subjects_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        subjects_frame.pack(expand=True, fill="both")
        
        subjects = list(QUESTIONS_DB.keys())
        colors_list = [COLORS["primary"], COLORS["accent"], COLORS["secondary"], "#5BAE9B", "#7AAEA0"]
        
        for i, subject in enumerate(subjects):
            btn = ctk.CTkButton(
                subjects_frame,
                text=f"📖 {subject}",
                command=lambda s=subject: self.start_quiz(s),
                width=280,
                height=55,
                font=ctk.CTkFont(size=16, weight="bold"),
                corner_radius=25,
                fg_color=colors_list[i % len(colors_list)],
                hover_color=COLORS["hover"]
            )
            btn.pack(pady=8, padx=20)
        
        back_btn = ctk.CTkButton(main_frame, text="◀️ НАЗАД", command=self.create_name_screen, width=200, height=40, font=ctk.CTkFont(size=14), corner_radius=20, fg_color=COLORS["accent"], hover_color=COLORS["hover"])
        back_btn.pack(pady=20)
    
    def start_quiz(self, subject):
        self.selected_subject = subject
        questions_full = QUESTIONS_DB[subject]
        if len(questions_full) > 10:
            self.questions = random.sample(questions_full, 10)
        else:
            self.questions = questions_full
        self.current_question = 0
        self.score = 0
        self.user_answers = []
        self.user_choices = [-1] * len(self.questions)
        self.show_question()
    
    def show_question(self):
        self.clear_window()
        
        q_data = self.questions[self.current_question]
        
        main_frame = ctk.CTkFrame(self.window, fg_color=COLORS["card"], corner_radius=20)
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        progress_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["secondary"], corner_radius=10, height=35)
        progress_frame.pack(fill="x", padx=30, pady=(20, 15))
        progress_frame.pack_propagate(False)
        
        progress = f"Вопрос {self.current_question + 1} из {len(self.questions)}"
        ctk.CTkLabel(progress_frame, text=progress, font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_light"]).pack(expand=True)
        
        subject_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["primary"], corner_radius=12, height=40)
        subject_frame.pack(pady=(0, 20))
        subject_frame.pack_propagate(False)
        ctk.CTkLabel(subject_frame, text=f"📚 {self.selected_subject}", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_light"]).pack(padx=20, pady=5)
        
        question_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["bg"], corner_radius=15)
        question_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(question_frame, text=q_data["question"], font=ctk.CTkFont(size=18, weight="bold"), text_color=COLORS["text_dark"], wraplength=800, justify="center").pack(padx=20, pady=20)
        
        self.answer_var = ctk.IntVar(value=self.user_choices[self.current_question])
        
        options_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        options_frame.pack(fill="both", expand=True, padx=20)
        
        for i, option in enumerate(q_data["options"]):
            radio_btn = ctk.CTkRadioButton(
                options_frame,
                text=option,
                variable=self.answer_var,
                value=i,
                font=ctk.CTkFont(size=14),
                fg_color=COLORS["accent"],
                hover_color=COLORS["primary"],
                text_color=COLORS["text_dark"]
            )
            radio_btn.pack(anchor="w", pady=8, padx=30)
        
        nav_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        nav_frame.pack(pady=(20, 10))
        
        if self.current_question > 0:
            back_btn = ctk.CTkButton(
                nav_frame, 
                text="◀️ НАЗАД", 
                command=self.prev_question, 
                width=120, 
                height=40, 
                font=ctk.CTkFont(size=13, weight="bold"), 
                corner_radius=20, 
                fg_color=COLORS["accent"], 
                hover_color=COLORS["hover"]
            )
            back_btn.pack(side="left", padx=10)
        
        next_text = "✅ ЗАВЕРШИТЬ" if self.current_question == len(self.questions) - 1 else "➡️ ДАЛЕЕ"
        next_btn = ctk.CTkButton(
            nav_frame, 
            text=next_text, 
            command=self.next_question, 
            width=150, 
            height=40, 
            font=ctk.CTkFont(size=13, weight="bold"), 
            corner_radius=20, 
            fg_color=COLORS["primary"], 
            hover_color=COLORS["hover"]
        )
        next_btn.pack(side="left", padx=10)
    
    def prev_question(self):
        self.user_choices[self.current_question] = self.answer_var.get()
        self.current_question -= 1
        self.show_question()
    
    def next_question(self):
        selected = self.answer_var.get()
        if selected == -1:
            messagebox.showwarning("Внимание", "Выберите вариант ответа!")
            return
        
        self.user_choices[self.current_question] = selected
        
        q_data = self.questions[self.current_question]
        is_correct = (selected == q_data["correct"])
        
        if len(self.user_answers) <= self.current_question:
            self.user_answers.append({
                "question": q_data["question"],
                "user_answer_text": q_data["options"][selected],
                "correct_answer_text": q_data["options"][q_data["correct"]],
                "is_correct": is_correct
            })
            if is_correct:
                self.score += 1
        
        if self.current_question + 1 < len(self.questions):
            self.current_question += 1
            self.show_question()
        else:
            self.show_results()
    
    def show_results(self):
        self.clear_window()
        
        self.window.geometry("1200x900")
        
        main_frame = ctk.CTkFrame(self.window, fg_color=COLORS["card"], corner_radius=20)
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        title_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["primary"], corner_radius=15, height=80)
        title_frame.pack(fill="x", padx=30, pady=(20, 15))
        title_frame.pack_propagate(False)
        
        ctk.CTkLabel(title_frame, text="🏆 РЕЗУЛЬТАТЫ КВИЗА 🏆", font=ctk.CTkFont(size=26, weight="bold"), text_color=COLORS["text_light"]).pack(expand=True)
        
        info_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["bg"], corner_radius=12)
        info_frame.pack(fill="x", padx=30, pady=(0, 15))
        
        ctk.CTkLabel(info_frame, text=f"Ученик: {self.player_name}", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_dark"]).pack(pady=(10, 5))
        ctk.CTkLabel(info_frame, text=f"Предмет: {self.selected_subject}", font=ctk.CTkFont(size=14), text_color=COLORS["text_dark"]).pack(pady=(0, 10))
        
        result_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["secondary"], corner_radius=15)
        result_frame.pack(pady=10, padx=30, fill="x")
        
        result_text = f"{self.score} / {len(self.questions)}"
        percent = (self.score / len(self.questions)) * 100
        
        ctk.CTkLabel(result_frame, text=f"⭐ Ваш результат: {result_text}", font=ctk.CTkFont(size=22, weight="bold"), text_color=COLORS["text_light"]).pack(pady=10)
        
        if percent >= 90:
            grade = "5 (Отлично!)"
            grade_color = COLORS["success"]
        elif percent >= 70:
            grade = "4 (Хорошо)"
            grade_color = "#F39C12"
        elif percent >= 50:
            grade = "3 (Удовлетворительно)"
            grade_color = "#E67E22"
        else:
            grade = "2 (Нужно повторить!)"
            grade_color = COLORS["error"]
        
        ctk.CTkLabel(result_frame, text=f"Оценка: {grade}", font=ctk.CTkFont(size=16, weight="bold"), text_color=grade_color).pack(pady=(0, 12))
        
        details_label = ctk.CTkLabel(main_frame, text="📋 ДЕТАЛИ ОТВЕТОВ:", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["primary"])
        details_label.pack(anchor="w", padx=30, pady=(10, 5))
        
        details_frame = ctk.CTkScrollableFrame(main_frame, fg_color=COLORS["bg"], corner_radius=10, height=280)
        details_frame.pack(fill="both", expand=True, padx=30, pady=(0, 15))
        
        for i, ans in enumerate(self.user_answers):
            answer_frame = ctk.CTkFrame(details_frame, fg_color=COLORS["card"], corner_radius=10, border_width=1, border_color=COLORS["secondary"])
            answer_frame.pack(fill="x", padx=5, pady=5)
            
            status_color = COLORS["success"] if ans["is_correct"] else COLORS["error"]
            status_text = "✅ ПРАВИЛЬНО" if ans["is_correct"] else "❌ НЕПРАВИЛЬНО"
            status_frame = ctk.CTkFrame(answer_frame, fg_color=status_color, corner_radius=5, height=25)
            status_frame.pack(fill="x", padx=8, pady=(5, 0))
            status_frame.pack_propagate(False)
            ctk.CTkLabel(status_frame, text=status_text, font=ctk.CTkFont(size=11, weight="bold"), text_color="white").pack(expand=True)
            
            q_text = ans["question"][:80] + "..." if len(ans["question"]) > 80 else ans["question"]
            ctk.CTkLabel(answer_frame, text=f"Вопрос {i+1}: {q_text}", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["text_dark"], wraplength=900, justify="left").pack(anchor="w", padx=10, pady=(5, 3))
            
            ctk.CTkLabel(answer_frame, text=f"📌 Ваш ответ: {ans['user_answer_text']}", font=ctk.CTkFont(size=10), text_color=COLORS["text_dark"], wraplength=900, justify="left").pack(anchor="w", padx=10)
            
            ctk.CTkLabel(answer_frame, text=f"✅ Правильный ответ: {ans['correct_answer_text']}", font=ctk.CTkFont(size=10), text_color=COLORS["success"], wraplength=900, justify="left").pack(anchor="w", padx=10, pady=(0, 5))
        
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(side="bottom", fill="x", pady=(0, 20), padx=30)
        
        replay_btn = ctk.CTkButton(
            buttons_frame, 
            text="🔄 ПРОЙТИ ЗАНОВО", 
            command=lambda: self.start_quiz(self.selected_subject), 
            width=180, 
            height=45, 
            font=ctk.CTkFont(size=13, weight="bold"), 
            corner_radius=22, 
            fg_color=COLORS["success"], 
            hover_color=COLORS["hover"]
        )
        replay_btn.pack(side="left", padx=10, pady=10, expand=True)
        
        categories_btn = ctk.CTkButton(
            buttons_frame, 
            text="📚 К КАТЕГОРИЯМ", 
            command=self.create_subject_screen, 
            width=180, 
            height=45, 
            font=ctk.CTkFont(size=13, weight="bold"), 
            corner_radius=22, 
            fg_color=COLORS["accent"], 
            hover_color=COLORS["hover"]
        )
        categories_btn.pack(side="left", padx=10, pady=10, expand=True)
        
        exit_btn = ctk.CTkButton(
            buttons_frame, 
            text="🚪 ВЫХОД", 
            command=self.window.destroy, 
            width=150, 
            height=45, 
            font=ctk.CTkFont(size=13, weight="bold"), 
            corner_radius=22, 
            fg_color=COLORS["error"], 
            hover_color="#C0392B"
        )
        exit_btn.pack(side="left", padx=10, pady=10, expand=True)

if __name__ == "__main__":
    if QUESTIONS_DB is None:
        messagebox.showerror("Ошибка", "Не удалось загрузить вопросы из базы данных.\nПроверьте подключение к SQL Server.")
    else:
        app = QuizApp()
        app.run()