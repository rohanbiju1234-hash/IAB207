"""
Populates fridaynight.db with sample data so markers don't need to create
their own test data.

    python seed_data.py

Wipes and re-creates the database each run - safe for local development.
Do NOT run this against the live PythonAnywhere database after deployment,
since it will delete any real data that's been added.
"""
from datetime import date, time, datetime, timedelta, timezone

from fridaynight import create_app, db
from fridaynight.models import User, Event, Booking, Comment

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    michael = User(first_name='Michael', last_name='Nguyen', email='michael@example.com',
                    contact_number='0400111222', street_address='12 River St, Brisbane QLD')
    sara = User(first_name='Sara', last_name='Ahmed', email='sara@example.com',
                contact_number='0400333444', street_address='4 Park Ave, Brisbane QLD')
    liam = User(first_name='Liam', last_name='Osei', email='liam@example.com',
                contact_number='0400555666', street_address='9 Hill Rd, Brisbane QLD')
    priya = User(first_name='Priya', last_name='Patel', email='priya@example.com',
                 contact_number='0400777888', street_address='27 Bay St, Brisbane QLD')

    for user in (michael, sara, liam, priya):
        user.set_password('password123')
    db.session.add_all([michael, sara, liam, priya])
    db.session.commit()

    today = date.today()

    events = [
        Event(title='Riverside Jazz Night', artist='The Boathouse Trio', category='Jazz',
              description='Join us on the Boathouse deck for an evening of live jazz overlooking the river. '
                          'Doors open at 6:30 PM, seating for up to 180 guests.',
              image_filename='jazz.webp', venue='The Boathouse, Riverside',
              event_date=today + timedelta(days=7), start_time=time(19, 0), end_time=time(22, 30),
              capacity=180, ticket_price=35.00, status=Event.STATUS_OPEN,
              acknowledgement_type=Event.ACK_GENERIC, owner=michael),

        Event(title='Amped Up: Rock Night', artist='Amped Up', category='Rock',
              description='A high-energy night of rock covers and originals at the Civic Convention Centre.',
              image_filename='rock.avif', venue='Civic Convention Centre',
              event_date=today + timedelta(days=14), start_time=time(20, 0), end_time=time(23, 0),
              capacity=300, ticket_price=45.00, status=Event.STATUS_OPEN,
              acknowledgement_type=Event.ACK_ENHANCED,
              traditional_custodians='the Turrbal and Yugara peoples',
              acknowledgement_text='We acknowledge the Turrbal and Yugara peoples, the Traditional Custodians '
                                    'of the land on which this event is held, and pay our respects to their '
                                    'Elders past, present and emerging.',
              owner=michael),

        Event(title='Hip-Hop Block Party', artist='DJ Nova', category='Hip-Hop',
              description='An outdoor block party with local hip-hop artists and a full sound rig.',
              image_filename='hiphop.jpg', venue='Northside Gallery',
              event_date=today + timedelta(days=20), start_time=time(18, 0), end_time=time(23, 0),
              capacity=250, ticket_price=30.00, status=Event.STATUS_CANCELLED,
              acknowledgement_type=Event.ACK_NONE, owner=sara),

        # capacity deliberately tiny so this event demonstrates the sold-out flow
        Event(title='Neon Nights EDM Rave', artist='Various DJs', category='EDM',
              description='Lights, lasers and a night full of EDM in the Old Quarter Laneway. Very limited capacity.',
              image_filename='edm-rave.jpg', venue='Old Quarter Laneway',
              event_date=today + timedelta(days=25), start_time=time(21, 0), end_time=time(2, 0),
              capacity=2, ticket_price=55.00, status=Event.STATUS_SOLD_OUT,
              acknowledgement_type=Event.ACK_NONE, owner=sara),

        Event(title='Aksomaniac R&B Evening', artist='Aksomaniac', category='R&B',
              description='A smooth, intimate R&B evening on the Bayside Esplanade.',
              image_filename='randb.webp', venue='Bayside Esplanade',
              event_date=today + timedelta(days=30), start_time=time(19, 30), end_time=time(22, 0),
              capacity=150, ticket_price=40.00, status=Event.STATUS_OPEN,
              acknowledgement_type=Event.ACK_GENERIC, owner=michael),

        # event_date in the past, to demonstrate the Inactive status
        Event(title='Rock Revival Tribute Night', artist='Rock Revival', category='Rock',
              description='A tribute night celebrating classic rock anthems, from a couple of weeks back.',
              image_filename='rock2.avif', venue='Coworking Hall, Level 2',
              event_date=today - timedelta(days=5), start_time=time(19, 0), end_time=time(22, 0),
              capacity=100, ticket_price=25.00, status=Event.STATUS_INACTIVE,
              acknowledgement_type=Event.ACK_NONE, owner=sara),

        Event(title='Late Night Jazz & Wine', artist='Cara Lowe Quartet', category='Jazz',
              description='A more intimate jazz evening paired with a curated wine list. Small venue, book early.',
              image_filename='jazz.webp', venue='The Cellar Door, West End',
              event_date=today + timedelta(days=10), start_time=time(20, 0), end_time=time(23, 30),
              capacity=5, ticket_price=50.00, status=Event.STATUS_OPEN,
              acknowledgement_type=Event.ACK_ENHANCED,
              traditional_custodians='the Yuggera and Turrbal peoples',
              acknowledgement_text='This event is held on the lands of the Yuggera and Turrbal peoples. '
                                    'We recognise their continuing connection to this land and pay our '
                                    'respects to Elders past, present and emerging.',
              owner=priya),

        Event(title='Sunset Rooftop EDM Sessions', artist='Kilo & Frey', category='EDM',
              description='Golden-hour house and EDM on a rooftop bar overlooking the city.',
              image_filename='edm-rave.jpg', venue='Skyline Rooftop Bar',
              event_date=today + timedelta(days=18), start_time=time(17, 0), end_time=time(21, 0),
              capacity=120, ticket_price=38.00, status=Event.STATUS_OPEN,
              acknowledgement_type=Event.ACK_NONE, owner=liam),

        Event(title='Old Skool Hip-Hop Reunion', artist='DJ Nova & Friends', category='Hip-Hop',
              description='A throwback night celebrating 90s and 2000s hip-hop classics.',
              image_filename='hiphop.jpg', venue='Warehouse 12',
              event_date=today + timedelta(days=35), start_time=time(20, 0), end_time=time(1, 0),
              capacity=200, ticket_price=32.00, status=Event.STATUS_OPEN,
              acknowledgement_type=Event.ACK_GENERIC, owner=liam),

        Event(title='Soul & R&B Sundowner', artist='Nia Blake', category='R&B',
              description='A relaxed Sunday-evening R&B set on the esplanade lawns, family friendly earlier on.',
              image_filename='randb.webp', venue='Bayside Esplanade',
              event_date=today + timedelta(days=40), start_time=time(17, 30), end_time=time(20, 30),
              capacity=180, ticket_price=28.00, status=Event.STATUS_OPEN,
              acknowledgement_type=Event.ACK_NONE, owner=priya),

        Event(title='Garage Rock Underground', artist='The Static Kids', category='Rock',
              description='Raw, loud garage rock in a small underground venue. 18+.',
              image_filename='rock.avif', venue='The Basement, Fortitude Valley',
              event_date=today - timedelta(days=2), start_time=time(21, 0), end_time=time(23, 59),
              capacity=80, ticket_price=20.00, status=Event.STATUS_INACTIVE,
              acknowledgement_type=Event.ACK_NONE, owner=liam),

        Event(title='EDM New Year Warm-Up', artist='Various DJs', category='EDM',
              description='A big warm-up party ahead of the new year celebrations - cancelled due to venue issues.',
              image_filename='edm-rave.jpg', venue='Old Quarter Laneway',
              event_date=today + timedelta(days=50), start_time=time(21, 0), end_time=time(3, 0),
              capacity=300, ticket_price=60.00, status=Event.STATUS_CANCELLED,
              acknowledgement_type=Event.ACK_NONE, owner=priya),
    ]
    db.session.add_all(events)
    db.session.commit()

    e = {ev.title: ev for ev in events}

    db.session.add_all([
        Comment(body='Excited for this one!', author=sara, event=e['Riverside Jazz Night']),
        Comment(body='Getting tickets soon!', author=michael, event=e['Amped Up: Rock Night']),
        Comment(body='Is there parking nearby?', author=priya, event=e['Amped Up: Rock Night']),
        Comment(body='Went last year, so good - highly recommend.', author=liam, event=e['Aksomaniac R&B Evening']),
        Comment(body='Can\'t wait, the venue is beautiful.', author=sara, event=e['Late Night Jazz & Wine']),
        Comment(body='Missed out on tickets, hope they add more dates!', author=michael, event=e['Neon Nights EDM Rave']),
    ])

    def booked_days_ago(n):
        return datetime.now(timezone.utc) - timedelta(days=n)

    db.session.add_all([
        Booking(order_reference='FN-20260803-3391', ticket_type='Standard Admission', quantity=2,
                total_price=70.00, user=sara, event=e['Riverside Jazz Night'], booked_at=booked_days_ago(10)),
        Booking(order_reference='FN-20260721-1187', ticket_type='Standard Admission', quantity=1,
                total_price=40.00, user=michael, event=e['Aksomaniac R&B Evening'], booked_at=booked_days_ago(20)),
        Booking(order_reference='FN-20260810-4820', ticket_type='VIP', quantity=2,
                total_price=140.00, user=liam, event=e['Amped Up: Rock Night'], booked_at=booked_days_ago(6)),
        Booking(order_reference='FN-20260815-7742', ticket_type='Standard Admission', quantity=2,
                total_price=100.00, user=priya, event=e['Neon Nights EDM Rave'], booked_at=booked_days_ago(4)),
        Booking(order_reference='FN-20260818-2295', ticket_type='Standard Admission', quantity=3,
                total_price=114.00, user=sara, event=e['Sunset Rooftop EDM Sessions'], booked_at=booked_days_ago(2)),
        Booking(order_reference='FN-20260819-6631', ticket_type='Standard Admission', quantity=1,
                total_price=50.00, user=michael, event=e['Late Night Jazz & Wine'], booked_at=booked_days_ago(1)),
        Booking(order_reference='FN-20260701-1002', ticket_type='Standard Admission', quantity=4,
                total_price=80.00, user=liam, event=e['Rock Revival Tribute Night'], booked_at=booked_days_ago(30)),
    ])

    db.session.commit()
    print(f'Database seeded: {User.query.count()} users, {Event.query.count()} events, '
          f'{Comment.query.count()} comments, {Booking.query.count()} bookings.')
    print('Test logins (all use password123):')
    for u in (michael, sara, liam, priya):
        print(f'  {u.email}')