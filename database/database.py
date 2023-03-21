import datetime
import sqlite3

from client.utils import Customer


class Database:
    def __init__(self, db_name: str):
        self.conn = sqlite3.connect(f'./database/{db_name}.db')
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.cursor.connection.close()

    def create_tables(self):
        try:
            self.cursor.execute(f'CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, first_name TEXT, last_name TEXT)')
            self.cursor.execute(f'CREATE TABLE IF NOT EXISTS reservations (id INTEGER PRIMARY KEY AUTOINCREMENT, '
                                f'start DATETIME, end DATETIME, customer_id INTEGER REFERENCES customers(id))')
            return True
        except sqlite3.Error as e:
            print(e)
            return False
        finally:
            self.conn.commit()

    def insert_customer(self, customer: Customer):
        try:
            self.cursor.execute('INSERT INTO customers VALUES (?, ?, ?)', [None, customer.first_name,
                                                                           customer.last_name])
            return True
        except sqlite3.Error as e:
            print(e)
            return False
        finally:
            self.conn.commit()

    def get_customer_id(self, customer: Customer) -> int:
        try:
            self.cursor.execute('SELECT id FROM customers WHERE first_name=? AND last_name=?', [customer.first_name,
                                                                                                customer.last_name])
            id = self.cursor.fetchone()
            return id[0] if id else None
        except sqlite3.Error as e:
            print(e)
            return False

    def get_reservation_id(self, customer_id: int, date: datetime.datetime) -> int | None:
        reservation_datetime = date.strftime('%Y-%m-%d %H:%M')
        try:
            self.cursor.execute('SELECT id FROM reservations WHERE customer_id=? AND start=?', [customer_id,
                                                                                                reservation_datetime])
            id = self.cursor.fetchone()
            return id[0] if id else None
        except sqlite3.Error as e:
            print(e)
            return False

    def set_reservation(self, customer_id: int, date: datetime.datetime, duration: int):
        begin_datetime = date.strftime('%Y-%m-%d %H:%M')
        end_datetime = (date + datetime.timedelta(minutes=duration)).strftime('%Y-%m-%d %H:%M')
        try:
            self.cursor.execute('INSERT INTO reservations VALUES (null, ?, ?, ?)', [begin_datetime, end_datetime, customer_id])
            return True
        except sqlite3.Error as e:
            print(e)
            return False
        finally:
            self.conn.commit()

    def is_reservation_available_to_set(self, date: datetime.datetime, duration: int) -> bool:
        begin_date = date.strftime('%Y-%m-%d')
        end_date = (date + datetime.timedelta(minutes=duration)).strftime('%Y-%m-%d')
        begin_datetime = date.strftime('%Y-%m-%d %H:%M')
        end_datetime = (date + datetime.timedelta(minutes=duration)).strftime('%Y-%m-%d %H:%M')
        try:
            self.cursor.execute('WITH today AS (SELECT id, start, end FROM reservations WHERE DATE('
                                'start)=:begin_date OR DATE(end)=:end_date) SELECT start, end FROM today WHERE '
                                ':begin_datetime >= start AND :begin_datetime < end OR :end_datetime > '
                                'start AND '
                                ':end_datetime <= end OR start >= :begin_datetime AND start < :end_datetime',
                                {'begin_date': begin_date,
                                 'end_date':end_date,
                                 'begin_datetime': begin_datetime,
                                 'end_datetime': end_datetime})
            reservation_conflicts = self.cursor.fetchall()

            return False if reservation_conflicts else True
        except sqlite3.Error as e:
            print(e)
            return False

    def get_suggestion_available_time(self, date: datetime.datetime, duration: int) -> tuple:
        begin_date = date.strftime('%Y-%m-%d')
        begin_datetime = date.strftime('%Y-%m-%d %H:%M')
        begin_day_end = begin_date + ' ' + '23:59'
        begin_next_day = (date + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        try:
            self.cursor.execute("SELECT end FROM (WITH today AS ( SELECT * FROM (SELECT id, start, end FROM reservations "
                                "WHERE DATE(end)=:begin_date) UNION SELECT * FROM (SELECT id, start, end "
                                "FROM reservations WHERE DATE(end)=:begin_next_day ORDER BY END LIMIT 1) ORDER BY "
                                "END) SELECT end, round(((julianday((ifnull((SELECT start FROM today WHERE start >= t.end"
                                " ORDER BY start LIMIT 1), :begin_day_end))) - julianday(end)) * 86400) / 60)"
                                " AS free_time FROM today AS t WHERE free_time >= :duration AND"
                                " end > :begin_datetime ORDER BY end)",
                                {'begin_date': begin_date,
                                 'begin_datetime': begin_datetime,
                                 'begin_day_end':begin_day_end,
                                 'begin_next_day': begin_next_day,
                                 'duration': duration})
            suggested_time = self.cursor.fetchone()
            return suggested_time if suggested_time else None
        except sqlite3.Error as e:
            print(e)
            return False

    def is_customer_has_less_than_two_reservations_this_week(self, customer_id: int, date: datetime.datetime) -> bool:
        try:
            self.cursor.execute('SELECT count(customer_id) AS reservations, customer_id, STRFTIME("%W %Y", '
                                'start) AS week FROM reservations WHERE customer_id=? AND week=? GROUP BY '
                                'customer_id, week HAVING reservations >= 2;', [customer_id, date.strftime('%V %Y')])
            return True if self.cursor.fetchone() is None else False
        except sqlite3.Error as e:
            print(e)
            return False

    def cancel_reservation(self, reservation_id: int):
        try:
            self.cursor.execute('DELETE FROM reservations WHERE id=?', [reservation_id])
            return True
        except sqlite3.Error as e:
            print(e)
            return False
        finally:
            self.conn.commit()

    def get_reservations_for_this_date(self, date: datetime.date) -> tuple | None:
        try:
            self.cursor.execute('SELECT first_name, last_name, start, end FROM customers JOIN reservations ON '
                                'customers.id=customer_id WHERE DATE(start)=? ORDER BY start;',
                                [date.strftime('%Y-%m-%d')])
            reservations = self.cursor.fetchall()
            return reservations if reservations else None
        except sqlite3.Error as e:
            print(e)
            return False