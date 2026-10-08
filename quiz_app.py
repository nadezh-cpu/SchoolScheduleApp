import customtkinter as ctk
from tkinter import messagebox, ttk
import random
import sqlite3
import traceback
import sys
from datetime import datetime

# =============================================
# ОТЛАДКА
# =============================================
def show_error_and_exit():
    print("Ошибка в коде:")
    traceback.print_exc()
    input("Нажмите Enter для выхода...")
    sys.exit(1)

# =============================================
# ПОДКЛЮЧЕНИЕ К БД
# =============================================
DB_NAME = "SchoolQuizDB.db"

def init_database():
    """Создание таблиц при первом запуске"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT UNIQUE,
                password TEXT,
                full_name TEXT,
                role TEXT
            )
        ''')
        
        # Таблица результатов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS QuizResults (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_login TEXT,
                user_name TEXT,
                subject TEXT,
                score INTEGER,
                total INTEGER,
                percent REAL,
                grade TEXT,
                answers TEXT,
                date TEXT,
                FOREIGN KEY (user_login) REFERENCES Users(login)
            )
        ''')
        
        # Добавляем тестовых пользователей, если их нет
        cursor.execute("SELECT COUNT(*) FROM Users WHERE login='ученик'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO Users (login, password, full_name, role) VALUES (?, ?, ?, ?)",
                          ("ученик", "123", "Иван Петров", "student"))
        
        cursor.execute("SELECT COUNT(*) FROM Users WHERE login='учитель'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO Users (login, password, full_name, role) VALUES (?, ?, ?, ?)",
                          ("учитель", "admin", "Анна Сергеевна", "teacher"))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print("Ошибка инициализации БД:", e)

def save_quiz_result(user_login, user_name, subject, score, total, percent, grade, answers):
    """Сохранение результата в БД"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO QuizResults (user_login, user_name, subject, score, total, percent, grade, answers, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_login, user_name, subject, score, total, percent, grade, str(answers), datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("Ошибка сохранения результата:", e)
        return False

def get_user_results(login):
    """Получение результатов пользователя"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT subject, score, total, percent, grade, date, answers
            FROM QuizResults
            WHERE user_login=?
            ORDER BY date DESC
        ''', (login,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print("Ошибка получения результатов:", e)
        return []

def get_all_results():
    """Получение всех результатов (для учителя)"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_name, user_login, subject, score, total, percent, grade, date, answers
            FROM QuizResults
            ORDER BY date DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print("Ошибка получения всех результатов:", e)
        return []

def get_user_role(login, password):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM Users WHERE login=? AND password=?", (login, password))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print("Ошибка при работе с БД:", e)
        return None

def register_user(login, password, full_name, role):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Users (login, password, full_name, role) VALUES (?, ?, ?, ?)", 
                       (login, password, full_name, role))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print("Ошибка регистрации:", e)
        return False

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
    "hover": "#1A8A82",
    "warning": "#F39C12"
}

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

# =============================================
# БАЗА ВОПРОСОВ
# =============================================
QUESTIONS_DB = {
    "Литература": [
        {"question": "Что такое фольклор?", "options": ["Авторское произведение", "Устное народное творчество", "Письменная литература", "Научный труд"], "correct": 1},
        {"question": "Почему Татьяна, героиня рассказа 'Муму', поцеловала Герасима на прощанье?", "options": ["Она была влюблена в него", "Так она поблагодарила его за доброту", "Она прощалась с ним навсегда", "Она хотела его обидеть"], "correct": 1},
        {"question": "Среди перечисленных жанров выберите фольклорный?", "options": ["Роман", "Басня", "Повесть", "Рассказ"], "correct": 1},
        {"question": "Из какого произведения фрагмент: «Нрава она была весьма смирного...»?", "options": ["«Муму»", "«Тёплый хлеб»", "«Васюткино озеро»", "«В дурном обществе»"], "correct": 0},
        {"question": "Из какого произведения фрагмент: «Филька был молчаливый, недоверчивый...»?", "options": ["«Муму»", "«Тёплый хлеб»", "«Васюткино озеро»", "«В дурном обществе»"], "correct": 1},
        {"question": "Из какого произведения фрагмент: «Мальчик застыл. У него даже дух захватило...»?", "options": ["«Муму»", "«Тёплый хлеб»", "«Васюткино озеро»", "«В дурном обществе»"], "correct": 2},
        {"question": "Из какого произведения фрагмент: «Уж сколько раз твердили миру...»?", "options": ["«Ворона и Лисица»", "«Муму»", "«Васюткино озеро»", "«В дурном обществе»"], "correct": 0},
        {"question": "Поэт, который учился в Царскосельском лицее?", "options": ["Лермонтов", "Пушкин", "Некрасов", "Тютчев"], "correct": 1},
        {"question": "Кто написал стихотворение «На Волге»?", "options": ["Пушкин", "Лермонтов", "Некрасов", "Фет"], "correct": 2},
        {"question": "Назовите автора произведения «О чем говорят цветы»", "options": ["Ж.Санд", "Тургенев", "Чехов", "Толстой"], "correct": 0},
    ],
    "Математика": [
        {"question": "Какая цифра стоит в разряде сотен в записи числа 293457?", "options": ["2", "3", "4", "5"], "correct": 2},
        {"question": "Укажите верную математическую запись", "options": ["24057 > 240507", "24057 < 240507", "24057 = 240507"], "correct": 1},
        {"question": "Найдите сумму чисел 2377 и 923", "options": ["11607", "3300", "3290", "3200"], "correct": 1},
        {"question": "Какие из перечисленных чисел делятся на 8?", "options": ["16", "18", "24", "32"], "correct": 0},
        {"question": "Чему равно произведение чисел 36 и 35?", "options": ["10980", "1980", "1260", "188"], "correct": 2},
        {"question": "В парке 8 белых скамеек, а синих на 16 больше. Сколько синих скамеек в парке?", "options": ["128", "24", "8", "34"], "correct": 1},
        {"question": "Во сколько раз 400 меньше, чем 8000?", "options": ["В 7600 раз", "В 2000 раз", "В 200 раз", "В 20 раз"], "correct": 3},
        {"question": "Укажите верное равенство", "options": ["704 см = 74 м", "704 см = 70 м 4 см", "704 см = 7 м 4 см"], "correct": 2},
        {"question": "Каким действием находится неизвестное в уравнении: 806 : х = 31?", "options": ["Делением", "Умножением", "Вычитанием", "Сложением"], "correct": 0},
        {"question": "Турист прошел 25 км за 5 часов. С какой скоростью шел турист?", "options": ["125 км/ч", "25 км/ч", "20 км/ч", "5 км/ч"], "correct": 3},
    ],
    "Русский язык": [
        {"question": "В каком слове звуков меньше, чем букв?", "options": ["степная", "якорь", "мышь", "среда"], "correct": 2},
        {"question": "В каком слове все согласные звуки звонкие?", "options": ["берег", "песня", "лесной", "дружба"], "correct": 0},
        {"question": "Сколько слогов в слове «представление»?", "options": ["4", "5", "6", "3"], "correct": 1},
        {"question": "Слово, имеющее несколько лексических значений, называется", "options": ["однозначное", "многозначное", "синоним", "антоним"], "correct": 1},
        {"question": "В каком примере слово употреблено в переносном значении?", "options": ["лист падает", "смелый солдат", "степь спит", "золотой браслет"], "correct": 2},
        {"question": "Какая пара слов является синонимами?", "options": ["смелый – бесстрашный", "смелый – смельчак", "смелый – трусливый", "смелый – храбрость"], "correct": 0},
        {"question": "Основа какого слова состоит из приставки, корня и суффикса?", "options": ["грамотный", "побелка", "самолетик", "весенняя"], "correct": 1},
        {"question": "Какое из слов не является однокоренным слову «водичка»?", "options": ["вода", "водный", "водичку", "водяной"], "correct": 2},
        {"question": "Какое из существительных не является одушевленным?", "options": ["береза", "ребята", "учитель", "шофер"], "correct": 0},
        {"question": "Укажите глагол", "options": ["бег", "бегун", "бежать", "беговой"], "correct": 2},
    ],
    "Биология": [
        {"question": "Наука о живой природе", "options": ["География", "Физика", "Химия", "Биология"], "correct": 3},
        {"question": "Живые организмы, в отличие от тел неживой природы", "options": ["имеют массу", "способны к обмену веществ", "не состоят из химических элементов", "имеют форму"], "correct": 1},
        {"question": "Все живые организмы способны к", "options": ["росту", "передвижению на четырёх конечностях", "впитыванию воды корнями", "улавливанию солнечного света"], "correct": 0},
        {"question": "Самый простой увеличительный прибор", "options": ["микроскоп", "телескоп", "весы", "лупа"], "correct": 3},
        {"question": "Процесс фотосинтеза характерен для представителей царства", "options": ["Животные", "Растения", "Грибы", "Вирусы"], "correct": 1},
        {"question": "Животные способны к", "options": ["фотосинтезу", "накапливанию крахмала", "активному передвижению", "питанию неорганическими веществами"], "correct": 2},
        {"question": "Какое дерево имеет белую кору?", "options": ["Дуб", "Клен", "Береза", "Сосна"], "correct": 2},
        {"question": "Сколько ног у паука?", "options": ["4", "6", "8", "10"], "correct": 2},
        {"question": "Какое животное спит зимой?", "options": ["Заяц", "Волк", "Медведь", "Лиса"], "correct": 2},
        {"question": "Какой орган отвечает за зрение?", "options": ["Ухо", "Нос", "Глаз", "Кожа"], "correct": 2},
    ],
    "География": [
        {"question": "Какой океан первоначально назывался Восточным?", "options": ["Индийский океан", "Атлантический океан", "Тихий океан", "Северный Ледовитый"], "correct": 0},
        {"question": "На географических картах всего лишь двух стран мира Тихий океан обозначен как Великий. О каких странах идет речь?", "options": ["Великобритания и Германия", "Франция и Нидерланды", "Китай и Япония", "Россия и США"], "correct": 1},
        {"question": "Кто назвал Африку Африкой?", "options": ["Древние римляне", "Древние греки", "Древние скандинавы", "Древние египтяне"], "correct": 0},
        {"question": "Как переводится название «Австралия»?", "options": ["Центральная", "Северная", "Южная", "Восточная"], "correct": 2},
        {"question": "В названии какой части света присутствует древнегреческое слово, которое переводится как «медведица»?", "options": ["Африка", "Антарктида", "Евразия", "Америка"], "correct": 1},
        {"question": "Название самого большого в мире острова, почти полностью покрытого льдом, переводится как «зеленая страна». Что это за остров?", "options": ["Тасмания", "Шпицберген", "Гренландия", "Исландия"], "correct": 2},
        {"question": "В честь какого животного назван один из островов близ Австралии?", "options": ["Кенгуру", "Волка", "Лисы", "Коалы"], "correct": 0},
        {"question": "«Страна лапоногих» - что это?", "options": ["Гватемала", "Никарагуа", "Патагония, южная часть Аргентины", "Чили"], "correct": 2},
        {"question": "В море Сулавеси есть Таракан. Что это такое?", "options": ["Остров", "Животное", "Корабль", "Вулкан"], "correct": 0},
        {"question": "Где находится архипелаг Россиян?", "options": ["На Чукотке", "В Южной Полинезии", "На Камчатке", "В Карибском море"], "correct": 1},
    ],
}

# =============================================
# КЛАСС ВХОДА
# =============================================
class LoginApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Вход в КВИЗ")
        self.window.geometry("400x650")
        self.window.configure(fg_color=COLORS["bg"])
        self.create_widgets()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.window, fg_color=COLORS["card"], corner_radius=15)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="🎓 КВИЗ ДЛЯ 5 КЛАССА",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=COLORS["primary"]).pack(pady=(20, 5))

        ctk.CTkLabel(main_frame, text="Введите логин и пароль",
                     font=ctk.CTkFont(size=12),
                     text_color=COLORS["text_dark"]).pack(pady=(0, 15))

        self.login_entry = ctk.CTkEntry(main_frame, width=280, height=35,
                                        placeholder_text="Логин", font=ctk.CTkFont(size=12))
        self.login_entry.pack(pady=5)

        self.pass_entry = ctk.CTkEntry(main_frame, width=280, height=35,
                                       placeholder_text="Пароль", show="*", font=ctk.CTkFont(size=12))
        self.pass_entry.pack(pady=5)

        ctk.CTkButton(main_frame, text="🔓 ВОЙТИ", command=self.check_user,
                      width=250, height=40, font=ctk.CTkFont(size=13, weight="bold"),
                      corner_radius=20, fg_color=COLORS["primary"]).pack(pady=15)

        ctk.CTkButton(main_frame, text="📝 ЗАРЕГИСТРИРОВАТЬСЯ", command=self.open_register,
                      width=250, height=35, font=ctk.CTkFont(size=12, weight="bold"),
                      corner_radius=20, fg_color=COLORS["accent"]).pack(pady=5)

        info_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["bg"], corner_radius=8)
        info_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(info_frame, text="📋 Тестовые аккаунты:",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=COLORS["text_dark"]).pack(pady=(5, 2))

        ctk.CTkLabel(info_frame,
                     text="ученик / 123 → student\nучитель / admin → teacher",
                     font=ctk.CTkFont(size=9), justify="left",
                     text_color=COLORS["text_dark"]).pack(pady=(0, 5))

    def open_register(self):
        self.window.destroy()
        RegisterApp().run()

    def check_user(self):
        login = self.login_entry.get()
        pwd = self.pass_entry.get()
        role = get_user_role(login, pwd)
        if role:
            self.window.destroy()
            if role == "teacher":
                app = TeacherApp(login)
            else:
                app = QuizApp(role, login)
            app.run()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def run(self):
        self.window.mainloop()

# =============================================
# КЛАСС РЕГИСТРАЦИИ
# =============================================
class RegisterApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Регистрация")
        self.window.geometry("400x650")
        self.window.configure(fg_color=COLORS["bg"])
        self.create_widgets()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.window, fg_color=COLORS["card"], corner_radius=15)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="📝 РЕГИСТРАЦИЯ",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=COLORS["primary"]).pack(pady=(15, 5))

        ctk.CTkLabel(main_frame, text="Создайте аккаунт",
                     font=ctk.CTkFont(size=12),
                     text_color=COLORS["text_dark"]).pack(pady=(0, 10))

        ctk.CTkLabel(main_frame, text="Имя и фамилия:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=15)
        self.name_entry = ctk.CTkEntry(main_frame, width=280, height=35, placeholder_text="Иван Петров", font=ctk.CTkFont(size=12))
        self.name_entry.pack(pady=3)

        ctk.CTkLabel(main_frame, text="Логин:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=15, pady=(5,0))
        self.login_entry = ctk.CTkEntry(main_frame, width=280, height=35, placeholder_text="Логин", font=ctk.CTkFont(size=12))
        self.login_entry.pack(pady=3)

        ctk.CTkLabel(main_frame, text="Пароль:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=15, pady=(5,0))
        self.pass_entry = ctk.CTkEntry(main_frame, width=280, height=35, placeholder_text="Пароль", show="*", font=ctk.CTkFont(size=12))
        self.pass_entry.pack(pady=3)

        ctk.CTkLabel(main_frame, text="Роль:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=15, pady=(5,0))
        self.role_var = ctk.StringVar(value="student")
        role_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        role_frame.pack(pady=3)
        ctk.CTkRadioButton(role_frame, text="Ученик", variable=self.role_var, value="student", font=ctk.CTkFont(size=11)).pack(side="left", padx=8)
        ctk.CTkRadioButton(role_frame, text="Учитель", variable=self.role_var, value="teacher", font=ctk.CTkFont(size=11)).pack(side="left", padx=8)

        ctk.CTkButton(main_frame, text="🔓 ЗАРЕГИСТРИРОВАТЬСЯ", command=self.register,
                      width=250, height=40, font=ctk.CTkFont(size=13, weight="bold"),
                      corner_radius=20, fg_color=COLORS["success"]).pack(pady=15)

        ctk.CTkButton(main_frame, text="◀️ НАЗАД К ВХОДУ", command=self.back_to_login,
                      width=200, height=30, font=ctk.CTkFont(size=11),
                      corner_radius=15, fg_color=COLORS["accent"]).pack(pady=5)

    def register(self):
        full_name = self.name_entry.get().strip()
        login = self.login_entry.get().strip()
        password = self.pass_entry.get().strip()
        role = self.role_var.get()

        if not full_name or not login or not password:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        if register_user(login, password, full_name, role):
            messagebox.showinfo("Успех", f"Регистрация успешна!\nДобро пожаловать, {full_name}!")
            self.back_to_login()
        else:
            messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует!")

    def back_to_login(self):
        self.window.destroy()
        LoginApp().run()

    def run(self):
        self.window.mainloop()

# =============================================
# КЛАСС УЧИТЕЛЯ - ПРОСМОТР РЕЗУЛЬТАТОВ
# =============================================
class TeacherApp:
    def __init__(self, login):
        self.login = login
        self.window = ctk.CTk()
        self.window.title("📊 Панель учителя")
        self.window.geometry("400x700")
        self.window.configure(fg_color=COLORS["bg"])
        self.selected_result = None
        self.create_widgets()

    def create_widgets(self):
        self.clear_window()
        
        main_frame = ctk.CTkFrame(self.window, fg_color=COLORS["card"], corner_radius=15)
        main_frame.pack(expand=True, fill="both", padx=15, pady=15)
        
        # Заголовок
        title_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["primary"], corner_radius=12, height=50)
        title_frame.pack(fill="x", padx=15, pady=(10, 10))
        title_frame.pack_propagate(False)
        ctk.CTkLabel(title_frame, text="📊 РЕЗУЛЬТАТЫ УЧЕНИКОВ", 
                    font=ctk.CTkFont(size=16, weight="bold"), 
                    text_color=COLORS["text_light"]).pack(expand=True)
        
        # Кнопка обновления
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkButton(btn_frame, text="🔄 ОБНОВИТЬ", command=self.refresh_results,
                     width=120, height=30, font=ctk.CTkFont(size=11, weight="bold"),
                     corner_radius=15, fg_color=COLORS["accent"]).pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="🚪 ВЫХОД", command=self.window.destroy,
                     width=80, height=30, font=ctk.CTkFont(size=11, weight="bold"),
                     corner_radius=15, fg_color=COLORS["error"]).pack(side="right", padx=5)
        
        # Список результатов
        results = get_all_results()
        
        if not results:
            ctk.CTkLabel(main_frame, text="📭 Нет результатов", 
                        font=ctk.CTkFont(size=14), 
                        text_color=COLORS["text_dark"]).pack(pady=50)
            return
        
        # Скроллируемый список
        list_frame = ctk.CTkScrollableFrame(main_frame, fg_color=COLORS["bg"], corner_radius=8)
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        for result in results:
            user_name, user_login, subject, score, total, percent, grade, date, answers = result
            
            # Карточка результата
            card = ctk.CTkFrame(list_frame, fg_color=COLORS["card"], corner_radius=8, 
                               border_width=1, border_color=COLORS["secondary"])
            card.pack(fill="x", padx=5, pady=3)
            
            # Имя и предмет
            ctk.CTkLabel(card, text=f"👤 {user_name}", 
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=COLORS["text_dark"]).pack(anchor="w", padx=10, pady=(5, 0))
            
            ctk.CTkLabel(card, text=f"📚 {subject}  |  {date}", 
                        font=ctk.CTkFont(size=9),
                        text_color=COLORS["text_dark"]).pack(anchor="w", padx=10)
            
            # Результат и оценка
            result_frame = ctk.CTkFrame(card, fg_color=COLORS["bg"], corner_radius=5)
            result_frame.pack(fill="x", padx=10, pady=(5, 5))
            
            percent_color = COLORS["success"] if percent >= 70 else COLORS["warning"] if percent >= 50 else COLORS["error"]
            
            ctk.CTkLabel(result_frame, text=f"⭐ {score}/{total}  ({percent:.0f}%)", 
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=percent_color).pack(side="left", padx=5)
            
            # Оценка цветная
            grade_color = COLORS["success"] if "5" in grade else COLORS["warning"] if "4" in grade or "3" in grade else COLORS["error"]
            ctk.CTkLabel(result_frame, text=f"Оценка: {grade}", 
                        font=ctk.CTkFont(size=10, weight="bold"),
                        text_color=grade_color).pack(side="right", padx=5)
            
            # Кнопка "ДЕТАЛИ"
            ctk.CTkButton(card, text="📋 ДЕТАЛИ", 
                         command=lambda r=result: self.show_result_details(r),
                         width=80, height=25, font=ctk.CTkFont(size=9, weight="bold"),
                         corner_radius=10, fg_color=COLORS["primary"]).pack(pady=(0, 5))

    def show_result_details(self, result):
        """Показ деталей ответов ученика"""
        user_name, user_login, subject, score, total, percent, grade, date, answers = result
        
        # Создаём окно с деталями
        detail_window = ctk.CTkToplevel(self.window)
        detail_window.title(f"Детали - {user_name}")
        detail_window.geometry("400x650")
        detail_window.configure(fg_color=COLORS["bg"])
        detail_window.grab_set()
        
        main_frame = ctk.CTkFrame(detail_window, fg_color=COLORS["card"], corner_radius=15)
        main_frame.pack(expand=True, fill="both", padx=15, pady=15)
        
        # Заголовок
        title_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["primary"], corner_radius=12, height=40)
        title_frame.pack(fill="x", padx=15, pady=(10, 8))
        title_frame.pack_propagate(False)
        ctk.CTkLabel(title_frame, text=f"📋 ДЕТАЛИ: {user_name}", 
                    font=ctk.CTkFont(size=14, weight="bold"), 
                    text_color=COLORS["text_light"]).pack(expand=True)
        
        # Информация
        info_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["bg"], corner_radius=8)
        info_frame.pack(fill="x", padx=15, pady=(0, 8))
        ctk.CTkLabel(info_frame, text=f"Предмет: {subject}", 
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=COLORS["text_dark"]).pack(pady=(3, 1))
        ctk.CTkLabel(info_frame, text=f"Результат: {score}/{total} ({percent:.0f}%)  Оценка: {grade}", 
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS["text_dark"]).pack(pady=(0, 3))
        
        # Детали ответов
        try:
            answers_list = eval(answers)
        except:
            answers_list = []
        
        if answers_list:
            details_frame = ctk.CTkScrollableFrame(main_frame, fg_color=COLORS["bg"], corner_radius=8)
            details_frame.pack(fill="both", expand=True, padx=15, pady=(0, 8))
            
            for i, ans in enumerate(answers_list):
                answer_frame = ctk.CTkFrame(details_frame, fg_color=COLORS["card"], 
                                           corner_radius=5, border_width=1, border_color=COLORS["secondary"])
                answer_frame.pack(fill="x", padx=2, pady=2)
                
                status_color = COLORS["success"] if ans.get("is_correct", False) else COLORS["error"]
                status_text = "✅ ПРАВИЛЬНО" if ans.get("is_correct", False) else "❌ НЕПРАВИЛЬНО"
                
                status_frame = ctk.CTkFrame(answer_frame, fg_color=status_color, corner_radius=3, height=16)
                status_frame.pack(fill="x", padx=4, pady=(2, 0))
                status_frame.pack_propagate(False)
                ctk.CTkLabel(status_frame, text=status_text, font=ctk.CTkFont(size=8, weight="bold"), text_color="white").pack(expand=True)
                
                ctk.CTkLabel(answer_frame, text=f"Вопрос {i+1}: {ans.get('question', '')}", 
                            font=ctk.CTkFont(size=8, weight="bold"), 
                            text_color=COLORS["text_dark"], 
                            wraplength=350, justify="left").pack(anchor="w", padx=6, pady=(2, 1))
                
                ctk.CTkLabel(answer_frame, text=f"➡️ Ответ ученика: {ans.get('user_answer_text', '')}", 
                            font=ctk.CTkFont(size=7), 
                            text_color=COLORS["text_dark"], 
                            wraplength=350, justify="left").pack(anchor="w", padx=6)
                
                ctk.CTkLabel(answer_frame, text=f"✅ Правильный ответ: {ans.get('correct_answer_text', '')}", 
                            font=ctk.CTkFont(size=7), 
                            text_color=COLORS["success"], 
                            wraplength=350, justify="left").pack(anchor="w", padx=6, pady=(0, 2))
        else:
            ctk.CTkLabel(main_frame, text="Нет деталей ответов", 
                        font=ctk.CTkFont(size=12), 
                        text_color=COLORS["text_dark"]).pack(pady=30)
        
        # Кнопка закрытия
        ctk.CTkButton(main_frame, text="✖ ЗАКРЫТЬ", 
                     command=detail_window.destroy,
                     width=150, height=30, font=ctk.CTkFont(size=11, weight="bold"),
                     corner_radius=15, fg_color=COLORS["error"]).pack(pady=10)

    def refresh_results(self):
        """Обновление списка результатов"""
        self.create_widgets()

    def clear_window(self):
        for widget in self.window.winfo_children():
            widget.destroy()

    def run(self):
        self.window.mainloop()

# =============================================
# ОСНОВНОЙ КЛАСС КВИЗА
# =============================================
class QuizApp:
    def __init__(self, role, login):
        self.role = role
        self.login = login
        self.player_name = self.get_user_name(login)
        self.window = ctk.CTk()
        self.window.title("🎓 КВИЗ - 5 класс")
        self.window.geometry("400x700")
        self.window.configure(fg_color=COLORS["bg"])
        
        self.selected_subject = ""
        self.current_question = 0
        self.score = 0
        self.user_answers = []
        self.questions = []
        self.user_choices = []
        
        self.create_subject_screen()
    
    def get_user_name(self, login):
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT full_name FROM Users WHERE login=?", (login,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else login
        except:
            return login
    
    def clear_window(self):
        for widget in self.window.winfo_children():
            widget.destroy()
    
    def create_subject_screen(self):
        self.clear_window()
        self.window.geometry("400x700")
        main_frame = ctk.CTkFrame(self.window, fg_color=COLORS["card"], corner_radius=15)
        main_frame.pack(expand=True, fill="both", padx=15, pady=15)
        
        title_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["secondary"], corner_radius=12, height=50)
        title_frame.pack(fill="x", padx=15, pady=(15, 10))
        title_frame.pack_propagate(False)
        
        ctk.CTkLabel(title_frame, text="🧠 ВЫБИРАЕМ КАТЕГОРИЮ",
                     font=ctk.CTkFont(size=16, weight="bold"), 
                     text_color=COLORS["text_light"]).pack(expand=True)
        
        ctk.CTkLabel(main_frame, text=f"👤 {self.player_name}",
                     font=ctk.CTkFont(size=12), 
                     text_color=COLORS["text_dark"]).pack(pady=(5, 5))
        
        ctk.CTkLabel(main_frame, text="Выбери предмет:",
                     font=ctk.CTkFont(size=14, weight="bold"), 
                     text_color=COLORS["text_dark"]).pack(pady=(5, 10))
        
        subjects_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        subjects_frame.pack(expand=True, fill="both")
        
        subjects = ["Литература", "Математика", "Русский язык", "Биология", "География"]
        colors_list = [COLORS["primary"], COLORS["accent"], COLORS["secondary"], "#5BAE9B", "#7AAEA0"]
        
        for i, subject in enumerate(subjects):
            btn = ctk.CTkButton(
                subjects_frame,
                text=f"📖 {subject}",
                command=lambda s=subject: self.start_quiz(s),
                width=220,
                height=40,
                font=ctk.CTkFont(size=13, weight="bold"),
                corner_radius=18,
                fg_color=colors_list[i % len(colors_list)],
                hover_color=COLORS["hover"]
            )
            btn.pack(pady=5, padx=15)
        
        # Кнопка "МОИ РЕЗУЛЬТАТЫ" для ученика
        if self.role == "student":
            results_btn = ctk.CTkButton(main_frame, text="📊 МОИ РЕЗУЛЬТАТЫ", 
                                       command=self.show_my_results,
                                       width=200, height=32, font=ctk.CTkFont(size=12, weight="bold"),
                                       corner_radius=15, fg_color=COLORS["secondary"])
            results_btn.pack(pady=5)
        
        exit_btn = ctk.CTkButton(main_frame, text="🚪 ВЫХОД", command=self.window.destroy,
                                 width=160, height=32, font=ctk.CTkFont(size=12),
                                 corner_radius=15, fg_color=COLORS["error"])
        exit_btn.pack(pady=10)
    
    def show_my_results(self):
        """Показ результатов ученика"""
        self.clear_window()
        main_frame = ctk.CTkFrame(self.window, fg_color=COLORS["card"], corner_radius=15)
        main_frame.pack(expand=True, fill="both", padx=15, pady=15)
        
        title_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["primary"], corner_radius=12, height=50)
        title_frame.pack(fill="x", padx=15, pady=(10, 10))
        title_frame.pack_propagate(False)
        ctk.CTkLabel(title_frame, text="📊 МОИ РЕЗУЛЬТАТЫ", 
                    font=ctk.CTkFont(size=16, weight="bold"), 
                    text_color=COLORS["text_light"]).pack(expand=True)
        
        results = get_user_results(self.login)
        
        if not results:
            ctk.CTkLabel(main_frame, text="📭 Вы ещё не проходили тесты", 
                        font=ctk.CTkFont(size=14), 
                        text_color=COLORS["text_dark"]).pack(pady=50)
        else:
            list_frame = ctk.CTkScrollableFrame(main_frame, fg_color=COLORS["bg"], corner_radius=8)
            list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            
            for result in results:
                subject, score, total, percent, grade, date, answers = result
                
                card = ctk.CTkFrame(list_frame, fg_color=COLORS["card"], corner_radius=8, 
                                   border_width=1, border_color=COLORS["secondary"])
                card.pack(fill="x", padx=5, pady=3)
                
                ctk.CTkLabel(card, text=f"📚 {subject}", 
                            font=ctk.CTkFont(size=11, weight="bold"),
                            text_color=COLORS["text_dark"]).pack(anchor="w", padx=10, pady=(5, 0))
                
                ctk.CTkLabel(card, text=f"📅 {date}", 
                            font=ctk.CTkFont(size=9),
                            text_color=COLORS["text_dark"]).pack(anchor="w", padx=10)
                
                result_frame = ctk.CTkFrame(card, fg_color=COLORS["bg"], corner_radius=5)
                result_frame.pack(fill="x", padx=10, pady=(5, 5))
                
                percent_color = COLORS["success"] if percent >= 70 else COLORS["warning"] if percent >= 50 else COLORS["error"]
                
                ctk.CTkLabel(result_frame, text=f"⭐ {score}/{total}  ({percent:.0f}%)", 
                            font=ctk.CTkFont(size=11, weight="bold"),
                            text_color=percent_color).pack(side="left", padx=5)
                
                grade_color = COLORS["success"] if "5" in grade else COLORS["warning"] if "4" in grade or "3" in grade else COLORS["error"]
                ctk.CTkLabel(result_frame, text=f"Оценка: {grade}", 
                            font=ctk.CTkFont(size=10, weight="bold"),
                            text_color=grade_color).pack(side="right", padx=5)
        
        ctk.CTkButton(main_frame, text="◀️ НАЗАД", command=self.create_subject_screen,
                     width=150, height=32, font=ctk.CTkFont(size=12, weight="bold"),
                     corner_radius=15, fg_color=COLORS["accent"]).pack(pady=10)
    
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
        self.window.geometry("400x700")
        q_data = self.questions[self.current_question]
        main_frame = ctk.CTkFrame(self.window, fg_color=COLORS["card"], corner_radius=15)
        main_frame.pack(expand=True, fill="both", padx=15, pady=15)
        
        progress_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["secondary"], corner_radius=8, height=28)
        progress_frame.pack(fill="x", padx=15, pady=(10, 8))
        progress_frame.pack_propagate(False)
        progress = f"Вопрос {self.current_question + 1} из {len(self.questions)}"
        ctk.CTkLabel(progress_frame, text=progress, font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["text_light"]).pack(expand=True)
        
        subject_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["primary"], corner_radius=10, height=30)
        subject_frame.pack(pady=(0, 10))
        subject_frame.pack_propagate(False)
        ctk.CTkLabel(subject_frame, text=f"📚 {self.selected_subject}", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["text_light"]).pack(padx=15, pady=3)
        
        question_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["bg"], corner_radius=10)
        question_frame.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkLabel(question_frame, text=q_data["question"], font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_dark"], wraplength=350, justify="center").pack(padx=10, pady=12)
        
        self.answer_var = ctk.IntVar(value=self.user_choices[self.current_question])
        options_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        options_frame.pack(fill="both", expand=True, padx=10)
        for i, option in enumerate(q_data["options"]):
            radio_btn = ctk.CTkRadioButton(
                options_frame,
                text=option,
                variable=self.answer_var,
                value=i,
                font=ctk.CTkFont(size=12),
                fg_color=COLORS["accent"],
                hover_color=COLORS["primary"],
                text_color=COLORS["text_dark"]
            )
            radio_btn.pack(anchor="w", pady=5, padx=10)
        
        nav_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        nav_frame.pack(pady=(10, 5))
        if self.current_question > 0:
            back_btn = ctk.CTkButton(nav_frame, text="◀️ НАЗАД", command=self.prev_question, 
                                     width=80, height=30, font=ctk.CTkFont(size=11, weight="bold"), 
                                     corner_radius=15, fg_color=COLORS["accent"])
            back_btn.pack(side="left", padx=5)
        next_text = "✅ ЗАВЕРШИТЬ" if self.current_question == len(self.questions) - 1 else "➡️ ДАЛЕЕ"
        next_btn = ctk.CTkButton(nav_frame, text=next_text, command=self.next_question, 
                                 width=100, height=30, font=ctk.CTkFont(size=11, weight="bold"), 
                                 corner_radius=15, fg_color=COLORS["primary"])
        next_btn.pack(side="left", padx=5)
    
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
        self.window.geometry("400x750")
        main_frame = ctk.CTkFrame(self.window, fg_color=COLORS["card"], corner_radius=15)
        main_frame.pack(expand=True, fill="both", padx=15, pady=15)
        
        # Заголовок
        title_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["primary"], corner_radius=12, height=40)
        title_frame.pack(fill="x", padx=15, pady=(10, 8))
        title_frame.pack_propagate(False)
        ctk.CTkLabel(title_frame, text="🏆 РЕЗУЛЬТАТЫ", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLORS["text_light"]).pack(expand=True)
        
        # Информация об ученике и предмете
        info_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["bg"], corner_radius=8)
        info_frame.pack(fill="x", padx=15, pady=(0, 6))
        ctk.CTkLabel(info_frame, text=f"Ученик: {self.player_name}", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["text_dark"]).pack(pady=(3, 1))
        ctk.CTkLabel(info_frame, text=f"Предмет: {self.selected_subject}", font=ctk.CTkFont(size=10), text_color=COLORS["text_dark"]).pack(pady=(0, 3))
        
        # Результат и оценка
        result_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["secondary"], corner_radius=10)
        result_frame.pack(pady=6, padx=15, fill="x")
        
        result_text = f"{self.score} / {len(self.questions)}"
        percent = (self.score / len(self.questions)) * 100
        ctk.CTkLabel(result_frame, text=f"⭐ {result_text}", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLORS["text_light"]).pack(pady=4)
        
        if percent >= 90:
            grade = "5 (Отлично!)"
            grade_color = COLORS["success"]
        elif percent >= 70:
            grade = "4 (Хорошо)"
            grade_color = COLORS["warning"]
        elif percent >= 50:
            grade = "3 (Удовлетворительно)"
            grade_color = COLORS["warning"]
        else:
            grade = "2 (Нужно повторить!)"
            grade_color = COLORS["error"]
        ctk.CTkLabel(result_frame, text=f"Оценка: {grade}", font=ctk.CTkFont(size=12, weight="bold"), text_color=grade_color).pack(pady=(0, 4))
        
        # Сохраняем результат в БД
        save_quiz_result(self.login, self.player_name, self.selected_subject, 
                        self.score, len(self.questions), percent, grade, self.user_answers)
        
        details_label = ctk.CTkLabel(main_frame, text="📋 ДЕТАЛИ ОТВЕТОВ:", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["primary"])
        details_label.pack(anchor="w", padx=15, pady=(4, 3))
        
        # Скроллируемый фрейм для деталей
        details_frame = ctk.CTkScrollableFrame(main_frame, fg_color=COLORS["bg"], corner_radius=8, height=180)
        details_frame.pack(fill="both", expand=True, padx=15, pady=(0, 5))
        
        # Добавляем каждый ответ в детали
        for i, ans in enumerate(self.user_answers):
            # Фрейм для ответа
            answer_frame = ctk.CTkFrame(details_frame, fg_color=COLORS["card"], corner_radius=5, border_width=1, border_color=COLORS["secondary"])
            answer_frame.pack(fill="x", padx=2, pady=2)
            
            # Статус ответа (правильно/неправильно)
            status_color = COLORS["success"] if ans["is_correct"] else COLORS["error"]
            status_text = "✅ ПРАВИЛЬНО" if ans["is_correct"] else "❌ НЕПРАВИЛЬНО"
            status_frame = ctk.CTkFrame(answer_frame, fg_color=status_color, corner_radius=3, height=16)
            status_frame.pack(fill="x", padx=4, pady=(2, 0))
            status_frame.pack_propagate(False)
            ctk.CTkLabel(status_frame, text=status_text, font=ctk.CTkFont(size=8, weight="bold"), text_color="white").pack(expand=True)
            
            # Текст вопроса
            ctk.CTkLabel(answer_frame, text=f"Вопрос {i+1}: {ans['question']}", 
                        font=ctk.CTkFont(size=8, weight="bold"), 
                        text_color=COLORS["text_dark"], 
                        wraplength=330, justify="left").pack(anchor="w", padx=6, pady=(2, 1))
            
            # Ответ пользователя
            ctk.CTkLabel(answer_frame, text=f"➡️ Ваш ответ: {ans['user_answer_text']}", 
                        font=ctk.CTkFont(size=7), 
                        text_color=COLORS["text_dark"], 
                        wraplength=330, justify="left").pack(anchor="w", padx=6)
            
            # Правильный ответ
            ctk.CTkLabel(answer_frame, text=f"✅ Правильный ответ: {ans['correct_answer_text']}", 
                        font=ctk.CTkFont(size=7), 
                        text_color=COLORS["success"], 
                        wraplength=330, justify="left").pack(anchor="w", padx=6, pady=(0, 2))

        # Кнопки внизу
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(side="bottom", fill="x", pady=(0, 8), padx=15)

        # Кнопка "ЗАНОВО"
        replay_btn = ctk.CTkButton(buttons_frame, text="🔄 ЗАНОВО",
                                   command=lambda: self.start_quiz(self.selected_subject),
                                   width=80, height=28, font=ctk.CTkFont(size=9, weight="bold"),
                                   corner_radius=12, fg_color=COLORS["success"])
        replay_btn.pack(side="left", padx=3, pady=3, expand=True)

        # Кнопка "К КАТЕГОРИЯМ"
        categories_btn = ctk.CTkButton(buttons_frame, text="📚 К КАТЕГОРИЯМ",
                                       command=self.create_subject_screen,
                                       width=90, height=28, font=ctk.CTkFont(size=9, weight="bold"),
                                       corner_radius=12, fg_color=COLORS["accent"])
        categories_btn.pack(side="left", padx=3, pady=3, expand=True)

        # Кнопка "ВЫХОД"
        exit_btn = ctk.CTkButton(buttons_frame, text="🚪 ВЫХОД", 
                                 command=self.window.destroy,
                                 width=70, height=28, font=ctk.CTkFont(size=9, weight="bold"),
                                 corner_radius=12, fg_color=COLORS["error"])
        exit_btn.pack(side="left", padx=3, pady=3, expand=True)

    def run(self):
        self.window.mainloop()

# =============================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# =============================================
if __name__ == "__main__":
    try:
        init_database()  # Инициализация БД при первом запуске
        app = LoginApp()
        app.run()
    except Exception:
        show_error_and_exit()