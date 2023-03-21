from datetime import datetime, date, timedelta
from typing import Generator

class Customer:
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Reservation:
    def __init__(self, customer_first_name: str, customer_last_name: str, reservation_start: str,
                 reservation_end: str):
        self.customer_first_name = customer_first_name
        self.customer_last_name = customer_last_name
        self.reservation_start = datetime.strptime(reservation_start, '%Y-%m-%d %H:%M')
        self.reservation_end = datetime.strptime(reservation_end, '%Y-%m-%d %H:%M')

    def __str__(self):
        return f'{self.customer_first_name} {self.customer_last_name} ' \
               f'{self.reservation_start.strftime("%d.%m.%Y %H:%M")} - ' \
               f'{self.reservation_end.strftime("%d.%m.%Y %H:%M")}'

def get_dates_from_range(from_date: date, to_date: date) -> Generator[date, None, None]:
    for day in range((to_date - from_date).days + 1):
        yield from_date + timedelta(days=day)

def is_datetime_less_than_hour_from_now(dt: datetime) -> bool:
    return True if datetime.now() + timedelta(hours=1) > dt else False

def get_customer_from_user():
    try:
        return Customer(*(input('Provide \'Name Surname\': ')).title().split())
    except TypeError as e:
        print('Provided text is incorrect!')
        return None


def get_date_from_user(dt=False) -> datetime | date:
    try:
        if dt:
            return datetime.strptime(input('Provide date (dd.mm.yyyy hh:mm): '), '%d.%m.%Y %H:%M')
        else:
            return datetime.strptime(input('Provide date (dd.mm.yyyy): '), '%d.%m.%Y').date()
    except ValueError as e:
        print('Provided date is incorrect!')
        return None

def get_dates_range_from_user() -> [date, date]:
    print('Provide range of dates')
    from_date, to_date = None, None
    while from_date is None or to_date is None or from_date > to_date:
        print('From Date:')
        from_date = get_date_from_user()
        if from_date is None:
            continue
        print('To date:')
        to_date = get_date_from_user()
        if to_date is None:
            continue

        if from_date > to_date:
            print('To date can\'t be before from date')
    return from_date, to_date

def choosing_menu(options: list, question: str, include_exit=True):
    if include_exit:
        options.append('Exit')
    option = None
    while option is None:
        print(question)
        for i, v in enumerate(options, start=1):
            print(f'\t{i}. {v}')
        try:
            option = int(input('Select: '))
            if option <= 0:
                print('Selected option is invalid!')
                option = None
                continue

            options[option - 1]
        except IndexError:
            print('Selected option is invalid!')
            option = None
        except ValueError:
            print('It has to be int!')
            option = None
    return option - 1
