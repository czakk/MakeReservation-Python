import pytest
import string
import random
import client.utils as utils

@pytest.fixture()
def customer_fixture():
    ctr = utils.Customer(f'Test{"".join(random.choices(string.ascii_uppercase, k=5))}', 'Test')
    return ctr

class TestReservation:
    def test_object_representation(self, customer_fixture):
        res = utils.Reservation(customer_fixture.first_name, customer_fixture.last_name, '2023-05-05 05:05',
                                '2023-05-05 06:05')
        assert str(res) == f'{customer_fixture.first_name} {customer_fixture.last_name} 05.05.2023 05:05 - 05.05.2023 06:05'