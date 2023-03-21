import csv
from client import utils
import json

from database.database import Database

db = Database('schedule')
db.create_tables()

def make_reservation():
    print('Make a reservation')
    customer = None
    while customer is None:
        customer = utils.get_customer_from_user()
    customer_id = db.get_customer_id(customer)
    if customer_id is None:
        db.insert_customer(customer)
        customer_id = db.get_customer_id(customer)

    print('When would You like to book?')
    date = None
    while date is None:
        date = utils.get_date_from_user(dt=True)

    if utils.is_datetime_less_than_hour_from_now(date):
        print('Date is less than one hour from now!')
        return

    if db.is_customer_has_less_than_two_reservations_this_week(customer_id, date) is False:
        print('You already booked court two times this week. If you want to cancel one, use \'Cancel Reservation\'')
        return

    duration_options = [30, 60, 90] if date.hour < 17 else [30, 60]
    duration = duration_options[utils.choosing_menu(duration_options, 'How long would You like to book court?',
                                                    include_exit=False)]

    if db.is_reservation_available_to_set(date, duration):
        db.set_reservation(customer_id, date, duration)
        print('You booked court!')
    else:
        suggested_date = db.get_suggestion_available_time(date, duration)
        if suggested_date is None:
            print('No available time for today')
            return
        datetime_suggested_date = utils.datetime.strptime(suggested_date[0], '%Y-%m-%d %H:%M')
        match utils.choosing_menu(['Yes', 'No'], f'The time you chose is unavailable, would you like to make a '
                                                 f'reservation for {datetime_suggested_date.strftime("%d.%m.%Y %H:%M")} '
                                                 f'instead?', include_exit=False):
            case 0:
                db.set_reservation(customer_id, datetime_suggested_date, duration)
                print('You booked court!')
            case 1:
                return

def cancel_reservation():
    print('Customer Name and Surname')
    customer = utils.get_customer_from_user()
    if customer is None:
        return
    customer_id = db.get_customer_id(customer)
    if db.get_customer_id(customer) is None:
        print(f'{customer} is unknown!')
        return

    print('Date and hour of reservation that You would like to cancel')
    date = utils.get_date_from_user(dt=True)
    reservation_id = db.get_reservation_id(customer_id, date)
    if reservation_id is None:
        print(f'{customer} doesn\'t has a reservation on {date.strftime("%d.%m.%Y %H:%M")}')
        return

    if utils.is_datetime_less_than_hour_from_now(date):
        print('You can\'t cancel a reservation less than one hour')
        return
    db.cancel_reservation(reservation_id)
    print('Reservation canceled!')

def print_schedule():
    today = utils.datetime.now().date()
    yesterday = today - utils.timedelta(days=1)
    tomorrow = today + utils.timedelta(days=1)

    from_date, to_date = utils.get_dates_range_from_user()

    for date in utils.get_dates_from_range(from_date=from_date, to_date=to_date):
        if date == today:
            operator = 'Today'
        elif date == yesterday:
            operator = 'Yesterday'
        elif date == tomorrow:
            operator = 'Tomorrow'
        else:
            operator = '%A'

        print(date.strftime(f'\n{operator}, %d.%m.%Y:'))

        reservations = db.get_reservations_for_this_date(date)
        if reservations is None:
            print('No reservations')
            continue
        for reservation in (utils.Reservation(*x) for x in reservations):
            print(f'* {reservation}')

def export_to_json():
    from_date, to_date = utils.get_dates_range_from_user()

    data = {
        date.strftime('%d.%m.%Y'):
                [
                    {
                        'name': f'{reservation.customer_first_name} {reservation.customer_last_name}',
                        'start_time': reservation.reservation_start.strftime('%H:%M'),
                        'end_time': reservation.reservation_end.strftime('%H:%M')
                    }
                    for reservation in (utils.Reservation(*x) for x in db.get_reservations_for_this_date(date))
                ]
            if db.get_reservations_for_this_date(date) is not None else []
            for date in utils.get_dates_from_range(from_date=from_date, to_date=to_date)
    }

    with open(f'./results/{from_date.strftime("%d.%m.%Y")}-{to_date.strftime("%d.%m.%Y")}.json', 'w',
              encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=3)

def export_to_csv():
    from_date, to_date = utils.get_dates_range_from_user()

    with open(f'./results/{from_date.strftime("%d.%m.%Y")}-{to_date.strftime("%d.%m.%Y")}.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'start_time', 'end_time'])
        for date in utils.get_dates_from_range(from_date=from_date, to_date=to_date):
            reservations = db.get_reservations_for_this_date(date)
            if reservations is None:
                continue

            reservations = [utils.Reservation(*x) for x in db.get_reservations_for_this_date(date)]
            for reservation in reservations:
                writer.writerow([f'{reservation.customer_first_name} {reservation.customer_last_name}',
                                 reservation.reservation_start.strftime('%d.%m.%Y %H:%M'),
                                 reservation.reservation_end.strftime('%d.%m.%Y %H:%M')])

def save_to_file():
    match utils.choosing_menu(['CSV', 'JSON'], 'In which format You want to save?'):
        case 0:
            export_to_csv()
        case 1:
            export_to_json()
        case _:
            return
    print('Check \'results\' folder')
