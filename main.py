import json
import random

FILENAME = "branch.json"


# Вспомогательная функция: загрузка данных из файла
def load_json():
    with open(FILENAME, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


# Вспомогательная функция: сохранение данных обратно в файл
def save_json(data):
    with open(FILENAME, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ФУНКЦИЯ АВТОМАТИЧЕСКОЙ ГЕНЕРАЦИИ СМЕН ПРИ ЗАПУСКЕ
def randomize_shifts_on_startup():
    data = load_json()

    # Собираем список ID всех сотрудников, кроме Руководителя (директор за кассой не стоит)
    cashier_ids = [
        emp_id for emp_id, info in data["employees"].items()
        if info["role"] != "Руководитель"
    ]

    # Если в базе есть кассиры и есть отчеты по сменам
    if cashier_ids and data["shift_reports"]:
        num_reports = len(data["shift_reports"])

        # Выбираем случайных неповторяющихся сотрудников для текущих отчетов
        if len(cashier_ids) >= num_reports:
            selected_employees = random.sample(cashier_ids, num_reports)
        else:
            selected_employees = [random.choice(cashier_ids) for _ in range(num_reports)]

        statuses = ["Излишек", "Недостача", "Без отклонений"]

        # Проходим по каждому отчету и меняем сотрудника, суммы и статус
        for (rep_id, rep_info), random_emp_id in zip(data["shift_reports"].items(), selected_employees):
            rep_info["employee_id"] = random_emp_id
            chosen_status = random.choice(statuses)
            rep_info["status"] = chosen_status

            # Генерируем случайную сумму от 100 до 3000 тенге (шагом по 100 тг)
            if chosen_status == "Излишек":
                rep_info["surplus"] = float(random.randint(1, 30) * 100)
                rep_info["shortage"] = 0.0
            elif chosen_status == "Недостача":
                rep_info["surplus"] = 0.0
                rep_info["shortage"] = float(random.randint(1, 30) * 100)
            else:
                rep_info["surplus"] = 0.0
                rep_info["shortage"] = 0.0

        save_json(data)
        print("\n[СИСТЕМА]: При запуске данные смен (сотрудники, излишки и недостачи) были случайно обновлены!")


# 1. ФУНКЦИЯ ЧТЕНИЯ ДАННЫХ (Read)
def read_data():
    data = load_json()

    print("\n=== ИНФОРМАЦИЯ О ФИЛИАЛЕ ===")
    print("Название:", data["branch_info"]["name"])
    print("Город:", data["branch_info"]["city"])
    print("Адрес:", data["branch_info"]["address"])
    print("Телефон:", data["branch_info"]["phone"])

    print("\n=== СПИСОК СОТРУДНИКОВ ===")
    for emp_id, emp_info in data["employees"].items():
        print(f"[{emp_id}] ФИО: {emp_info['full_name']} | "
              f"Должность: {emp_info['position']} | Роль: {emp_info['role']}")

    print("\n=== ОТЧЕТЫ ПО СМЕНАМ ===")
    for rep_id, rep_info in data["shift_reports"].items():
        emp_key = rep_info["employee_id"]
        if emp_key in data["employees"]:
            emp_name = data["employees"][emp_key]["full_name"]
        else:
            emp_name = "Неизвестный сотрудник"

        print(f"[{rep_id}] Дата: {rep_info['date']} | Сотрудник: {emp_name} ({emp_key}) | "
              f"Излишек: {rep_info['surplus']} тг | Недостача: {rep_info['shortage']} тг | "
              f"Статус: {rep_info['status']}")


# 2. ФУНКЦИЯ ДОБАВЛЕНИЯ ДАННЫХ (Create / Add)
def add_data():
    data = load_json()

    print("\nЧто вы хотите добавить?")
    print("1 - Нового сотрудника")
    print("2 - Новый отчет по смене")
    choice = input("Ваш выбор: ")

    if choice == "1":
        emp_id = input("Введите ключ сотрудника (например, emp_19): ")
        full_name = input("Введите ФИО сотрудника: ")
        position = input("Введите должность (Кассир дневной / Кассир ночной / Продавец-кассир СП): ")
        role = input("Введите роль (Руководитель / Старший кассир / Сотрудник): ")

        data["employees"][emp_id] = {
            "full_name": full_name,
            "position": position,
            "role": role
        }
        save_json(data)
        print(f"Сотрудник {full_name} успешно добавлен в файл!")

    elif choice == "2":
        rep_id = input("Введите ключ отчета (например, rep_104): ")
        date = input("Введите дату смены (ГГГГ-ММ-ДД): ")
        emp_id = input("Введите ID сотрудника (от emp_1 до emp_18): ")
        surplus = float(input("Введите сумму излишка (0, если нет): "))
        shortage = float(input("Введите сумму недостачи (0, если нет): "))

        if surplus > 0:
            status = "Излишек"
        elif shortage > 0:
            status = "Недостача"
        else:
            status = "Без отклонений"

        data["shift_reports"][rep_id] = {
            "date": date,
            "employee_id": emp_id,
            "surplus": surplus,
            "shortage": shortage,
            "status": status
        }
        save_json(data)
        print(f"Отчет {rep_id} успешно сохранен в файл!")
    else:
        print("Неверный выбор пункта.")


# 3. ФУНКЦИЯ РЕДАКТИРОВАНИЯ ДАННЫХ (Update / Edit)
def edit_data():
    data = load_json()

    print("\nЧто вы хотите отредактировать?")
    print("1 - Должность и роль сотрудника")
    print("2 - Финансовый результат в отчете по смене")
    print("3 - Адрес и телефон филиала")
    choice = input("Ваш выбор: ")

    if choice == "1":
        emp_id = input("Введите ID сотрудника для изменения (например, emp_6): ")
        if emp_id in data["employees"]:
            new_pos = input("Введите новую должность: ")
            new_role = input("Введите новую роль: ")
            data["employees"][emp_id]["position"] = new_pos
            data["employees"][emp_id]["role"] = new_role
            save_json(data)
            print("Данные сотрудника успешно обновлены!")
        else:
            print("Сотрудник с таким ID не найден.")

    elif choice == "2":
        rep_id = input("Введите ID отчета для изменения (например, rep_101): ")
        if rep_id in data["shift_reports"]:
            new_surplus = float(input("Введите новую сумму излишка: "))
            new_shortage = float(input("Введите новую сумму недостачи: "))

            data["shift_reports"][rep_id]["surplus"] = new_surplus
            data["shift_reports"][rep_id]["shortage"] = new_shortage

            if new_surplus > 0:
                data["shift_reports"][rep_id]["status"] = "Излишек"
            elif new_shortage > 0:
                data["shift_reports"][rep_id]["status"] = "Недостача"
            else:
                data["shift_reports"][rep_id]["status"] = "Без отклонений"

            save_json(data)
            print("Отчет по смене успешно отредактирован!")
        else:
            print("Отчет с таким ID не найден.")

    elif choice == "3":
        new_address = input("Введите новый адрес филиала: ")
        new_phone = input("Введите новый телефон филиала: ")
        data["branch_info"]["address"] = new_address
        data["branch_info"]["phone"] = new_phone
        save_json(data)
        print("Контактные данные филиала обновлены!")
    else:
        print("Неверный выбор пункта.")


# 4. ФУНКЦИЯ УДАЛЕНИЯ ДАННЫХ (Delete)
def delete_data():
    data = load_json()

    print("\nЧто вы хотите удалить?")
    print("1 - Сотрудника по ключу")
    print("2 - Отчет по смене по ключу")
    choice = input("Ваш выбор: ")

    if choice == "1":
        emp_id = input("Введите ID сотрудника для удаления (например, emp_18): ")
        if emp_id in data["employees"]:
            del data["employees"][emp_id]
            save_json(data)
            print(f"Сотрудник {emp_id} удален из базы.")
        else:
            print("Сотрудник с таким ID не найден.")

    elif choice == "2":
        rep_id = input("Введите ID отчета для удаления (например, rep_103): ")
        if rep_id in data["shift_reports"]:
            del data["shift_reports"][rep_id]
            save_json(data)
            print(f"Отчет {rep_id} удален из базы.")
        else:
            print("Отчет с таким ID не найден.")
    else:
        print("Неверный выбор пункта.")


# ГЛАВНЫЙ ЦИКЛ КОНСОЛЬНОГО ПРИЛОЖЕНИЯ
def main():
    # Автоматическое изменение сотрудников, излишков и недостач при каждом старте
    randomize_shifts_on_startup()

    while True:
        print("\n" + "=" * 45)
        print(" СИСТЕМА УПРАВЛЕНИЯ ФИЛИАЛОМ (РАБОТА С JSON)")
        print("=" * 45)
        print("1. Показать все данные из файла (Чтение)")
        print("2. Добавить сотрудника или отчет (Добавление)")
        print("3. Изменить существующие данные (Редактирование)")
        print("4. Удалить запись по ключу (Удаление)")
        print("0. Выход из программы")
        print("=" * 45)

        action = input("Выберите номер действия: ")

        if action == "1":
            read_data()
        elif action == "2":
            add_data()
        elif action == "3":
            edit_data()
        elif action == "4":
            delete_data()
        elif action == "0":
            print("Работа приложения завершена.")
            break
        else:
            print("Ошибка: введите цифру от 0 до 4!")


if __name__ == "__main__":
    main()