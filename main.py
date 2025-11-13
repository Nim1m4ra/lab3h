from models import Database, User, Courier, Admin, Order
from datetime import datetime

db = Database()

def login() -> dict | None:
    login_str = input("Введите login: ")
    password_hash = input("Введите password_hash: ")  # В реальности хэшировать, здесь для теста
    return db.authenticate(login_str, password_hash)

def client_menu(user: User):
    while True:
        print("\nМеню клиента:")
        print("1. Оформить заказ")
        print("2. Просмотреть свои заказы")
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
            for order in orders:
                print(f"Заказ #{order.order_id}: Адрес: {order.delivery_address}, Статус: {order.status}, Сумма: {order.total_amount}")
        elif choice == '3':
            break
        else:
            print("Неверный выбор.")

def courier_menu(courier: Courier):
    while True:
        print("\nМеню курьера:")
        print("1. Просмотреть доступные заказы")
        print("2. Принять заказ")
        print("3. Просмотреть свои заказы")
        print("4. Изменить статус заказа (in_delivery/delivered/cancelled)")
        print("5. Выйти")
        choice = input("Выберите опцию: ")
        if choice == '1':
            orders = db.get_available_orders()
            for order in orders:
                print(f"Заказ #{order.order_id}: Адрес: {order.delivery_address}, Сумма: {order.total_amount}")
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
            for order in orders:
                print(f"Заказ #{order.order_id}: Адрес: {order.delivery_address}, Статус: {order.status}")
        elif choice == '4':
            try:
                order_id = int(input("ID заказа: "))
            except ValueError:
                print("Ошибка: Введите целое число.")
                continue
            status = input("Новый статус (in_delivery/delivered/cancelled): ")
            if status not in ['in_delivery', 'delivered', 'cancelled']:
                print("Ошибка: Неверный статус.")
                continue
            db.update_order(order_id, status=status)
            print("Статус обновлен.")
        elif choice == '5':
            break
        else:
            print("Неверный выбор.")

def admin_menu(admin: Admin):
    while True:
        print("\nМеню администратора:")
        print("1. Просмотреть все заказы")
        print("2. Добавить курьера")
        print("3. Удалить курьера")
        print("4. Просмотреть курьеров")
        print("5. Выйти")
        choice = input("Выберите опцию: ")
        if choice == '1':
            orders = db.get_all_orders()
            for order in orders:
                print(f"Заказ #{order.order_id}: Клиент {order.user_id}, Курьер {order.courier_id}, Статус: {order.status}")
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
            for c in couriers:
                print(f"Курьер #{c.courier_id}: {c.name}, Статус: {c.status}")
        elif choice == '5':
            break
        else:
            print("Неверный выбор.")

def main():
    print("Добро пожаловать в систему доставки.")
    auth = login()
    if auth:
        role = auth['role']
        data = auth['data']
        if role == 'user':
            client_menu(data)
        elif role == 'courier':
            courier_menu(data)
        elif role == 'admin':
            admin_menu(data)
    else:
        print("Авторизация не удалась.")
    db.close()

if __name__ == "__main__":
    main()