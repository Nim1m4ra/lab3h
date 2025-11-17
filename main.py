from models import Database, User, Courier, Admin, Order
from datetime import datetime

db = Database()

def get_role_choice():
    while True:
        print("\nКто заходит в систему?")
        print("1. Администратор")
        print("2. Курьер")
        print("3. Пользователь (Клиент)")
        choice = input("Выберите номер: ")
        if choice == '1':
            return 'admin'
        elif choice == '2':
            return 'courier'
        elif choice == '3':
            return 'user'
        else:
            print("Неверный выбор. Попробуйте снова.")

def login(role: str) -> dict | None:
    login_str = input("Введите login: ")
    password_hash = input("Введите password_hash: ")  # В реальности хэшировать

    if role == 'user':
        db.cursor.execute('SELECT * FROM "User" WHERE login = ? AND password_hash = ?', (login_str, password_hash))
        row = db.cursor.fetchone()
        if row:
            return {'role': 'user', 'data': User(*row)}
    elif role == 'courier':
        db.cursor.execute('SELECT * FROM Courier WHERE login = ? AND password_hash = ?', (login_str, password_hash))
        row = db.cursor.fetchone()
        if row:
            return {'role': 'courier', 'data': Courier(*row)}
    elif role == 'admin':
        db.cursor.execute('SELECT * FROM Admin WHERE login = ? AND password_hash = ?', (login_str, password_hash))
        row = db.cursor.fetchone()
        if row:
            return {'role': 'admin', 'data': Admin(*row)}

    print("Неверные credentials или роль не соответствует аккаунту!")
    return None

def client_menu(user: User):
    while True:
        print("\nФункционал для клиента:")
        print("1. Оформление заказа на доставку товара")
        print("2. Просмотр своих заказов с текущими статусами")
        print("3. Выйти")
        choice = input("Выберите опцию: ")
        if choice == '1':
            delivery_addr = input("Адрес доставки: ")
            try:
                total_input = input("Сумма заказа (опционально, enter для пропуска): ")
                total_amount = float(total_input) if total_input else None
            except ValueError:
                print("Ошибка: Введите число или оставьте пустым.")
                continue
            order_id = db.create_order(user.user_id, delivery_addr, total_amount)
            print(f"Заказ #{order_id} создан.")
        elif choice == '2':
            orders = db.get_user_orders(user.user_id)
            if not orders:
                print("Нет заказов.")
            for order in orders:
                print(f"Заказ #{order.order_id}: Адрес: {order.delivery_address}, Статус: {order.status}, Сумма: {order.total_amount or 'Не указана'}")
        elif choice == '3':
            break
        else:
            print("Неверный выбор.")

def courier_menu(courier: Courier):
    while True:
        print("\nФункционал для курьера:")
        print("1. Просмотр доступных заказов")
        print("2. Принять заказ")
        print("3. Просмотр моих заказов")
        print("4. Отменить заказ / Изменить статус на 'доставлен'")
        print("5. Выйти")
        choice = input("Выберите опцию: ")
        if choice == '1':
            orders = db.get_available_orders()
            if not orders:
                print("Нет доступных заказов.")
            for order in orders:
                print(f"Заказ #{order.order_id}: Адрес: {order.delivery_address}, Сумма: {order.total_amount or 'Не указана'}")
        elif choice == '2':
            try:
                order_id = int(input("ID заказа для принятия: "))
            except ValueError:
                print("Ошибка: Введите целое число.")
                continue
            db.update_order(order_id, courier_id=courier.courier_id, status='accepted')
            print("Заказ принят.")
        elif choice == '3':
            orders = db.get_courier_orders(courier.courier_id)
            if not orders:
                print("Нет ваших заказов.")
            for order in orders:
                print(f"Заказ #{order.order_id}: Адрес: {order.delivery_address}, Статус: {order.status}")
        elif choice == '4':
            try:
                order_id = int(input("ID заказа: "))
            except ValueError:
                print("Ошибка: Введите целое число.")
                continue
            action = input("Действие (cancelled - отменить, delivered - доставлен, in_delivery - в доставке): ")
            if action not in ['cancelled', 'delivered', 'in_delivery']:
                print("Ошибка: Неверное действие.")
                continue
            db.update_order(order_id, status=action)
            print("Статус обновлен.")
        elif choice == '5':
            break
        else:
            print("Неверный выбор.")

def admin_menu(admin: Admin):
    while True:
        print("\nФункционал для администратора:")
        print("1. Просмотр всех заказов (и обработка: подтверждение/отклонение)")
        print("2. Добавление курьеров в систему")
        print("3. Удалить курьера")
        print("4. Просмотреть курьеров")
        print("5. Выйти")
        choice = input("Выберите опцию: ")
        if choice == '1':
            orders = db.get_all_orders()
            if not orders:
                print("Нет заказов.")
            for order in orders:
                print(f"Заказ #{order.order_id}: Клиент {order.user_id}, Курьер {order.courier_id or 'Не назначен'}, Статус: {order.status}")
            # Обработка (пример: подтверждение/отклонение)
            try:
                order_id = int(input("ID заказа для обработки (enter для пропуска): ") or 0)
                if order_id:
                    action = input("Действие (accepted - подтвердить, cancelled - отклонить): ")
                    if action in ['accepted', 'cancelled']:
                        db.update_order(order_id, status=action)
                        print("Заказ обработан.")
                    else:
                        print("Неверное действие.")
            except ValueError:
                print("Ошибка: Введите целое число.")
        elif choice == '2':
            login = input("Login курьера: ")
            password_hash = input("Password_hash: ")
            name = input("Name (опционально): ") or None
            phone = input("Phone (опционально): ") or None
            courier_id = db.create_courier(login, password_hash, name, phone, admin_id=admin.admin_id)
            print(f"Курьер #{courier_id} добавлен.")
        elif choice == '3':
            try:
                courier_id = int(input("ID курьера для удаления: "))
            except ValueError:
                print("Ошибка: Введите целое число.")
                continue
            db.delete_courier(courier_id)
            print("Курьер удален.")
        elif choice == '4':
            couriers = db.get_couriers_by_admin(admin.admin_id)
            if not couriers:
                print("Нет курьеров.")
            for c in couriers:
                print(f"Курьер #{c.courier_id}: {c.name or 'Без имени'}, Статус: {c.status}")
        elif choice == '5':
            break
        else:
            print("Неверный выбор.")

def main():
    print("Добро пожаловать в систему учета доставки заказов.")
    role = get_role_choice()
    auth = login(role)
    if auth:
        if auth['role'] == 'user':
            client_menu(auth['data'])
        elif auth['role'] == 'courier':
            courier_menu(auth['data'])
        elif auth['role'] == 'admin':
            admin_menu(auth['data'])
    else:
        print("Авторизация не удалась.")
    db.close()

if __name__ == "__main__":
    main()