import string
import pytest
import random
from database.database import Database, Customer, datetime


@pytest.fixture()
def customer_fixture():
    ctr = Customer(f'Test{"".join(random.choices(string.ascii_uppercase, k=5))}', 'Test')
    return ctr

class TestDatabase:
    db = Database('test')

    def test_database_connection(self):
        assert self.db.conn

    def test_create_tables(self):
        assert self.db.create_tables()

    def test_insert_customer(self, customer_fixture):
        assert self.db.insert_customer(customer_fixture)

    def test_get_customer_id(self, customer_fixture):
        id = self.db.get_customer_id(customer_fixture)
        assert id is None

        self.db.insert_customer(customer_fixture)
        self.db.cursor.execute('select max(id) from customers;')
        latest_customer_id = self.db.cursor.fetchone()[0]
        id = self.db.get_customer_id(customer_fixture)
        assert id == latest_customer_id

    def test_set_reservation(self, customer_fixture):
        self.db.insert_customer(customer_fixture)
        customer_id = self.db.get_customer_id(customer_fixture)

        assert self.db.set_reservation(customer_id, datetime.datetime(2023, 3, 1, 15, 0), 30)
        self.db.cursor.execute('select * from reservations where id=1;')
        reservation = self.db.cursor.fetchone()
        assert reservation == (1, '2023-03-01 15:00', '2023-03-01 15:30', customer_id)

        assert self.db.set_reservation(customer_id, datetime.datetime(2023, 5, 20, 23, 59), 60)
        self.db.cursor.execute('select * from reservations where id=2;')
        reservation = self.db.cursor.fetchone()
        assert reservation == (2, '2023-05-20 23:59', '2023-05-21 00:59', customer_id)

    def test_get_reservation_id(self, customer_fixture):
        self.db.insert_customer(customer_fixture)
        customer_id = self.db.get_customer_id(customer_fixture)
        self.db.set_reservation(customer_id, datetime.datetime(2023, 1, 1, 0, 0), 60)

        self.db.cursor.execute('select max(id) from reservations;')
        latest_reservation_id = self.db.cursor.fetchone()[0]
        reservation_id = self.db.get_reservation_id(customer_id, datetime.datetime(2023, 1, 1, 0, 0))
        assert reservation_id == latest_reservation_id

    def test_is_reservation_available_to_set(self):
        assert self.db.is_reservation_available_to_set(datetime.datetime(2023, 3, 1, 15, 30), 30)
        assert self.db.is_reservation_available_to_set(datetime.datetime(2023, 6, 13, 11, 0), 90)
        assert self.db.is_reservation_available_to_set(datetime.datetime(2023, 3, 1, 14, 31), 30) == False
        assert self.db.is_reservation_available_to_set(datetime.datetime(2023, 3, 1, 15, 20), 60) == False
        assert self.db.is_reservation_available_to_set(datetime.datetime(2023, 5, 20, 23, 50), 90) == False

    def test_get_suggest_available_time(self, customer_fixture):
        self.db.insert_customer(customer_fixture)
        customer_id = self.db.get_customer_id(customer_fixture)

        assert self.db.get_suggestion_available_time(datetime.datetime(2023, 3, 1, 15, 29), 30)
        assert self.db.get_suggestion_available_time(datetime.datetime(2023, 3, 1, 15, 29), 60)
        assert self.db.get_suggestion_available_time(datetime.datetime(2023, 3, 1, 15, 29), 90)

        self.db.set_reservation(customer_id, datetime.datetime(2023, 3, 1, 16, 1), 30)
        self.db.set_reservation(customer_id, datetime.datetime(2023, 3, 1, 17, 31), 60)
        assert self.db.get_suggestion_available_time(datetime.datetime(2023, 3, 1, 15, 29), 30) == ('2023-03-01 15:30',)
        assert self.db.get_suggestion_available_time(datetime.datetime(2023, 3, 1, 15, 29), 60) == ('2023-03-01 16:31',)
        assert self.db.get_suggestion_available_time(datetime.datetime(2023, 3, 1, 15, 29), 90) == ('2023-03-01 18:31',)

        self.db.set_reservation(customer_id, datetime.datetime(2023, 5, 21, 1, 0), 60 * 24)
        assert self.db.get_suggestion_available_time(datetime.datetime(2023, 5, 21, 0, 59), 30) is None
        assert self.db.get_suggestion_available_time(datetime.datetime(2023, 5, 21, 15, 30), 60) is None
        assert self.db.get_suggestion_available_time(datetime.datetime(2023, 5, 21, 18, 21), 90) is None

    def test_is_customer_has_less_than_two_reservations_this_week(self, customer_fixture):
        self.db.insert_customer(customer_fixture)
        customer_id = self.db.get_customer_id(customer_fixture)
        self.db.set_reservation(customer_id, datetime.datetime(2023, 5, 20, 0, 59), 60)
        self.db.set_reservation(customer_id, datetime.datetime(2023, 5, 20, 0, 59), 60)
        assert self.db.is_customer_has_less_than_two_reservations_this_week(customer_id, datetime.datetime(2023, 5,
                                                                                                           21, 1, 0)) == False
        assert self.db.is_customer_has_less_than_two_reservations_this_week(1, datetime.datetime(2023, 5, 20, 0, 0))

    def test_cancel_reservation(self, customer_fixture):
        self.db.insert_customer(customer_fixture)
        customer_id = self.db.get_customer_id(customer_fixture)

        date = datetime.datetime(2023, 2, 2, 15, 0)
        self.db.set_reservation(customer_id, date, 60)
        reservation_id = self.db.get_reservation_id(customer_id, date)
        assert self.db.cancel_reservation(reservation_id)
        assert self.db.get_reservation_id(customer_id, date) is None

    def test_get_reservations_for_this_date(self, customer_fixture):
        self.db.insert_customer(customer_fixture)
        customer_id = self.db.get_customer_id(customer_fixture)
        self.db.set_reservation(customer_id, datetime.datetime(2023, 7, 5, 0, 59), 60)
        self.db.set_reservation(customer_id, datetime.datetime(2023, 7, 5, 1, 59), 60)
        self.db.set_reservation(customer_id, datetime.datetime(2023, 7, 5, 2, 59), 60)
        assert self.db.get_reservations_for_this_date(datetime.date(2023, 7, 5)) == ([(customer_fixture.first_name,
                                                                                      customer_fixture.last_name,
                                                                                     '2023-07-05 00:59',
                                                                                     '2023-07-05 01:59'),
                                                                                     (customer_fixture.first_name,
                                                                                     customer_fixture.last_name,
                                                                                     '2023-07-05 01:59',
                                                                                     '2023-07-05 02:59'),
                                                                                     (customer_fixture.first_name,
                                                                                     customer_fixture.last_name,
                                                                                     '2023-07-05 02:59',
                                                                                     '2023-07-05 03:59')])
        assert self.db.get_reservations_for_this_date(datetime.date(2023, 7, 8)) is None

    def test_drop_table(self):
        self.db.cursor.execute('DROP TABLE customers')
        self.db.cursor.execute('DROP TABLE reservations')
        self.db.conn.commit()

