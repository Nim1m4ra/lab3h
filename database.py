import sqlite3
from datetime import datetime

# Подключение к БД (создаст файл, если не существует)
conn = sqlite3.connect('delivery.db')
cursor = conn.cursor()

# Создание таблицы User (Пользователь - клиент)
cursor.execute('''
CREATE TABLE IF NOT EXISTS "User" (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT,
    phone TEXT
)
''')

# Создание таблицы Courier (Курьер)
cursor.execute('''
CREATE TABLE IF NOT EXISTS Courier (
    courier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT,
    phone TEXT,
    status TEXT NOT NULL CHECK(status IN ('active', 'inactive')) DEFAULT 'active',
    admin_id INTEGER,
    FOREIGN KEY (admin_id) REFERENCES Admin(admin_id) ON DELETE SET NULL
)
''')

# Создание таблицы Admin (Администратор)
cursor.execute('''
CREATE TABLE IF NOT EXISTS Admin (
    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT
)
''')

# Создание таблицы Order (Заказ)
cursor.execute('''
CREATE TABLE IF NOT EXISTS "Order" (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    courier_id INTEGER,
    status TEXT NOT NULL CHECK(status IN ('new', 'accepted', 'in_delivery', 'delivered', 'cancelled')) DEFAULT 'new',
    created_at DATETIME NOT NULL,
    delivery_address TEXT NOT NULL,
    total_amount DECIMAL(10,2),
    FOREIGN KEY (user_id) REFERENCES "User"(user_id) ON DELETE CASCADE,
    FOREIGN KEY (courier_id) REFERENCES Courier(courier_id) ON DELETE SET NULL
)
''')

# Добавление тестовых записей в Admin
cursor.executemany('''
INSERT OR IGNORE INTO Admin (login, password_hash, name) VALUES (?, ?, ?)
''', [
    ('admin1', 'hash789', 'Admin One')
])

# Добавление тестовых записей в User
cursor.executemany('''
INSERT OR IGNORE INTO "User" (login, password_hash, name, phone) VALUES (?, ?, ?, ?)
''', [
    ('client1', 'hash123', 'Client One', '+123456789')
])

# Добавление тестовых записей в Courier (связь с admin)
cursor.executemany('''
INSERT OR IGNORE INTO Courier (login, password_hash, name, phone, status, admin_id) VALUES (?, ?, ?, ?, ?, ?)
''', [
    ('courier1', 'hash456', 'Courier One', '+987654321', 'active', 1)
])

# Добавление тестовых записей в Order
current_time = datetime.now().isoformat()
cursor.executemany('''
INSERT OR IGNORE INTO "Order" (user_id, courier_id, status, created_at, delivery_address, total_amount) VALUES (?, ?, ?, ?, ?, ?)
''', [
    (1, None, 'new', current_time, 'Moscow, Pushkina 2', 100.50),
    (1, 1, 'accepted', current_time, 'SPb, Palace 4', 200.00)
])

# Сохранение изменений
conn.commit()
conn.close()

print("База данных создана и тестовые данные добавлены.")