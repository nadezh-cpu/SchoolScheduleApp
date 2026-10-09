import os
from database import get_classes, get_schedule, test_connection

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear()
    print("=" * 60)
    print("       ШКОЛЬНОЕ РАСПИСАНИЕ")
    print("=" * 60)
    
    print("\n🔌 Проверка подключения...")
    if not test_connection():
        input("\nНажмите Enter для выхода...")
        return
    
    classes = get_classes()
    if not classes:
        print("❌ Нет классов")
        return
    
    while True:
        clear()
        print("=" * 60)
        print("       ШКОЛЬНОЕ РАСПИСАНИЕ")
        print("=" * 60)
        print("\nДоступные классы:")
        for i, c in enumerate(classes, 1):
            print(f"  {i}. {c} класс")
        print("  0. Выход")
        
        try:
            choice = int(input("\nВыберите класс: "))
            if choice == 0:
                print("\nДо свидания!")
                break
            class_name = classes[choice - 1]
        except:
            input("Неверный выбор. Нажмите Enter...")
            continue
        
        clear()
        print("=" * 60)
        print(f"РАСПИСАНИЕ ДЛЯ {class_name} КЛАССА")
        print("=" * 60)
        print("  1. Понедельник")
        print("  2. Вторник")
        print("  3. Среда")
        print("  4. Четверг")
        print("  5. Пятница")
        print("  0. Назад")
        
        try:
            day = int(input("\nВыберите день: "))
            if day == 0:
                continue
        except:
            input("Неверный выбор. Нажмите Enter...")
            continue
        
        days = ["", "ПН", "ВТ", "СР", "ЧТ", "ПТ"]
        
        clear()
        print("=" * 60)
        print(f"{class_name} класс, {days[day]}")
        print("=" * 60)
        
        rows = get_schedule(class_name, day)
        
        if not rows:
            print("\nНет расписания")
        else:
            print(f"\n{'Урок':<6} {'Начало':<8} {'Конец':<8} {'Предмет':<20} {'Учитель':<25} {'Каб':<6}")
            print("-" * 75)
            for r in rows:
                print(f"{r[0]:<6} {r[1]:<8} {r[2]:<8} {r[3]:<20} {r[4]:<25} {r[5]:<6}")
            print("-" * 75)
        
        input("\nНажмите Enter...")

if __name__ == "__main__":
    main()
    # Добавила изменение в ветви second для практической работы № 4