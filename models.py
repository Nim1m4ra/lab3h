from dataclasses import dataclass
import sqlite3
from typing import List, Optional
from datetime import datetime  # <-- ДОБАВЛЕНО ДЛЯ ИСПРАВЛЕНИЯ ОШИБКИ

@dataclass
class User:
    user_id: int
    login: str
    password_hash: str
    name: Optional[str]
    phone: Optional[str]

@dataclass
class Courier:
    courier_id: int
    login: str
    password_hash: str
    name: Optional[str]
    phone: Optional[str]
    status: str
    admin_id: Optional[int]

@dataclass
class Admin:
    admin_id: int
    login: str
    password_hash: str
    name: Optional[str]

@dataclass
class Order:
    order_id: int
    user_id: int
    courier_id: Optional[int]
    status: str
    created_at: str
    delivery_address: str
    total_amount: Optional[float]

class Database:
    def __init__(self, db_name: str = 'delivery.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    # Авторизация: поиск по login и password_hash в любой таблице
    def authenticate(self, login: str, password_hash: str) -> Optional[dict]:
        # Проверка в User
        self.cursor.execute('SELECT * FROM "User" WHERE login = ? AND password_hash = ?', (login, password_hash))
        row = self.cursor.fetchone()
        if row:
            return {'role': 'user', 'data': User(*row)}

        # Проверка в Courier
        self.cursor.execute('SELECT * FROM Courier WHERE login = ? AND password_hash = ?', (login, password_hash))
        row = self.cursor.fetchone()
        if row:
            return {'role': 'courier', 'data': Courier(*row)}

        # Проверка в Admin
        self.cursor.execute('SELECT * FROM Admin WHERE login = ? AND password_hash = ?', (login, password_hash))
        row = self.cursor.fetchone()
        if row:
            return {'role': 'admin', 'data': Admin(*row)}

        return None

    # CRUD for User
    def create_user(self, login: str, password_hash: str, name: str = None, phone: str = None) -> int:
        self.cursor.execute('INSERT INTO "User" (login, password_hash, name, phone) VALUES (?, ?, ?, ?)', (login, password_hash, name, phone))
        self.conn.commit()
        return self.cursor.lastrowid

    def read_user(self, user_id: int) -> Optional[User]:
        self.cursor.execute('SELECT * FROM "User" WHERE user_id = ?', (user_id,))
        row = self.cursor.fetchone()
        return User(*row) if row else None

    def update_user(self, user_id: int, login: str = None, password_hash: str = None, name: str = None, phone: str = None):
        updates = []
        params = []
        if login: updates.append('login = ?'); params.append(login)
        if password_hash: updates.append('password_hash = ?'); params.append(password_hash)
        if name: updates.append('name = ?'); params.append(name)
        if phone: updates.append('phone = ?'); params.append(phone)
        if updates:
            params.append(user_id)
            self.cursor.execute(f'UPDATE "User" SET {", ".join(updates)} WHERE user_id = ?', params)
            self.conn.commit()

    def delete_user(self, user_id: int):
        self.cursor.execute('DELETE FROM "User" WHERE user_id = ?', (user_id,))
        self.conn.commit()

    # CRUD for Courier
    def create_courier(self, login: str, password_hash: str, name: str = None, phone: str = None, status: str = 'active', admin_id: int = None) -> int:
        self.cursor.execute('INSERT INTO Courier (login, password_hash, name, phone, status, admin_id) VALUES (?, ?, ?, ?, ?, ?)', (login, password_hash, name, phone, status, admin_id))
        self.conn.commit()
        return self.cursor.lastrowid

    def read_courier(self, courier_id: int) -> Optional[Courier]:
        self.cursor.execute('SELECT * FROM Courier WHERE courier_id = ?', (courier_id,))
        row = self.cursor.fetchone()
        return Courier(*row) if row else None

    def update_courier(self, courier_id: int, login: str = None, password_hash: str = None, name: str = None, phone: str = None, status: str = None, admin_id: int = None):
        updates = []
        params = []
        if login: updates.append('login = ?'); params.append(login)
        if password_hash: updates.append('password_hash = ?'); params.append(password_hash)
        if name: updates.append('name = ?'); params.append(name)
        if phone: updates.append('phone = ?'); params.append(phone)
        if status: updates.append('status = ?'); params.append(status)
        if admin_id is not None: updates.append('admin_id = ?'); params.append(admin_id)
        if updates:
            params.append(courier_id)
            self.cursor.execute(f'UPDATE Courier SET {", ".join(updates)} WHERE courier_id = ?', params)
            self.conn.commit()

    def delete_courier(self, courier_id: int):
        self.cursor.execute('DELETE FROM Courier WHERE courier_id = ?', (courier_id,))
        self.conn.commit()

    # CRUD for Admin
    def create_admin(self, login: str, password_hash: str, name: str = None) -> int:
        self.cursor.execute('INSERT INTO Admin (login, password_hash, name) VALUES (?, ?, ?)', (login, password_hash, name))
        self.conn.commit()
        return self.cursor.lastrowid

    def read_admin(self, admin_id: int) -> Optional[Admin]:
        self.cursor.execute('SELECT * FROM Admin WHERE admin_id = ?', (admin_id,))
        row = self.cursor.fetchone()
        return Admin(*row) if row else None

    def update_admin(self, admin_id: int, login: str = None, password_hash: str = None, name: str = None):
        updates = []
        params = []
        if login: updates.append('login = ?'); params.append(login)
        if password_hash: updates.append('password_hash = ?'); params.append(password_hash)
        if name: updates.append('name = ?'); params.append(name)
        if updates:
            params.append(admin_id)
            self.cursor.execute(f'UPDATE Admin SET {", ".join(updates)} WHERE admin_id = ?', params)
            self.conn.commit()

    def delete_admin(self, admin_id: int):
        self.cursor.execute('DELETE FROM Admin WHERE admin_id = ?', (admin_id,))
        self.conn.commit()

    # CRUD for Order
    def create_order(self, user_id: int, delivery_address: str, total_amount: float = None, created_at: str = datetime.now().isoformat()) -> int:
        self.cursor.execute('''
        INSERT INTO "Order" (user_id, status, created_at, delivery_address, total_amount)
        VALUES (?, 'new', ?, ?, ?)
        ''', (user_id, created_at, delivery_address, total_amount))
        self.conn.commit()
        return self.cursor.lastrowid

    def read_order(self, order_id: int) -> Optional[Order]:
        self.cursor.execute('SELECT * FROM "Order" WHERE order_id = ?', (order_id,))
        row = self.cursor.fetchone()
        return Order(*row) if row else None

    def update_order(self, order_id: int, courier_id: Optional[int] = None, status: str = None):
        updates = []
        params = []
        if courier_id is not None:
            updates.append('courier_id = ?')
            params.append(courier_id)
        if status:
            updates.append('status = ?')
            params.append(status)
        if updates:
            params.append(order_id)
            self.cursor.execute(f'UPDATE "Order" SET {", ".join(updates)} WHERE order_id = ?', params)
            self.conn.commit()

    def delete_order(self, order_id: int):
        self.cursor.execute('DELETE FROM "Order" WHERE order_id = ?', (order_id,))
        self.conn.commit()

    # Слой доступа к данным (Views из ERD)
    def get_available_orders(self) -> List[Order]:  # Для курьера: status = 'new'
        self.cursor.execute('SELECT * FROM "Order" WHERE status = "new"')
        return [Order(*row) for row in self.cursor.fetchall()]

    def get_user_orders(self, user_id: int) -> List[Order]:  # Мои заказы пользователя
        self.cursor.execute('SELECT * FROM "Order" WHERE user_id = ?', (user_id,))
        return [Order(*row) for row in self.cursor.fetchall()]

    def get_courier_orders(self, courier_id: int) -> List[Order]:  # Мои заказы курьера: accepted, in_delivery
        self.cursor.execute('SELECT * FROM "Order" WHERE courier_id = ? AND status IN ("accepted", "in_delivery")', (courier_id,))
        return [Order(*row) for row in self.cursor.fetchall()]

    def get_all_orders(self) -> List[Order]:  # Для админа
        self.cursor.execute('SELECT * FROM "Order"')
        return [Order(*row) for row in self.cursor.fetchall()]

    # Дополнительно: Курьеры под админом
    def get_couriers_by_admin(self, admin_id: int) -> List[Courier]:
        self.cursor.execute('SELECT * FROM Courier WHERE admin_id = ?', (admin_id,))
        return [Courier(*row) for row in self.cursor.fetchall()]