"""Registration, login and logout edge-case checks (Member 1: Auth and User Management).

Run from the project folder (the one containing main.py):
    python tests\\test_register.py .

The checks register a few temporary users in the local database and delete them
again at the end, so the seeded data is left as it was.
"""
import sys

project = sys.argv[1] if len(sys.argv) > 1 else '.'
sys.path.insert(0, project)

from fridaynight import create_app, db          # noqa: E402
from fridaynight.models import User             # noqa: E402

failures = []


def check(name, condition):
    print(('PASS  ' if condition else 'FAIL  ') + name)
    if not condition:
        failures.append(name)


app = create_app()
app.config['WTF_CSRF_ENABLED'] = False   # the test client does not fetch CSRF tokens

DOMAIN = '@regtest.example'


def form(**overrides):
    data = {
        'first_name': 'Test', 'last_name': 'User', 'email': 'new' + DOMAIN,
        'contact_number': '0400000000', 'street_address': '1 Test St',
        'password': 'goodpass1', 'confirm_password': 'goodpass1',
    }
    data.update(overrides)
    return data


def user_count(email):
    with app.app_context():
        return User.query.filter_by(email=email.lower()).count()


def cleanup():
    with app.app_context():
        for u in User.query.filter(User.email.like('%' + DOMAIN)).all():
            db.session.delete(u)
        db.session.commit()


cleanup()   # in case an earlier run was interrupted
try:
    # ---- a valid registration ----
    c = app.test_client()
    r = c.post('/register', data=form(email='Valid' + DOMAIN.upper()))
    check('valid registration redirects to the login page', r.status_code == 302 and r.headers['Location'].endswith('/login'))
    check('email is stored in lower case', user_count('valid' + DOMAIN) == 1)
    with app.app_context():
        u = User.query.filter_by(email='valid' + DOMAIN).first()
        check('password is stored hashed, not as plain text', u.password_hash != 'goodpass1' and 'goodpass1' not in u.password_hash)
        check('stored password hash verifies the right password only', u.check_password('goodpass1') and not u.check_password('wrongpass'))

    # ---- duplicate email ----
    r = c.post('/register', data=form(email='VALID' + DOMAIN))
    check('duplicate email (any letter case) is rejected', r.status_code == 200 and b'already exists' in r.data)
    check('duplicate email does not create a second user', user_count('valid' + DOMAIN) == 1)

    # ---- password rules ----
    r = c.post('/register', data=form(email='mismatch' + DOMAIN, confirm_password='different1'))
    check('mismatched confirm password is rejected with a message', r.status_code == 200 and b'Passwords must match.' in r.data)
    check('mismatched confirm password creates no user', user_count('mismatch' + DOMAIN) == 0)

    r = c.post('/register', data=form(email='short' + DOMAIN, password='abc12', confirm_password='abc12'))
    check('password shorter than 6 characters is rejected with a message', r.status_code == 200 and b'at least 6 characters' in r.data)
    check('short password creates no user', user_count('short' + DOMAIN) == 0)

    # ---- email format ----
    for bad in ['notanemail', 'missing-at.example.com', 'two@@regtest.example', 'spaces in@regtest.example']:
        r = c.post('/register', data=form(email=bad))
        check(f'invalid email {bad!r} is rejected', r.status_code == 200 and b'Invalid email' in r.data)

    # ---- required fields ----
    for field in ['first_name', 'last_name', 'email', 'contact_number', 'street_address', 'password', 'confirm_password']:
        data = form(email='blank' + DOMAIN)
        data[field] = ''
        r = c.post('/register', data=data)
        check(f'blank {field} is rejected', r.status_code == 200 and b'This field is required' in r.data)
    check('no user was created by any blank-field attempt', user_count('blank' + DOMAIN) == 0)

    # ---- length limits (the database column sizes) ----
    r = c.post('/register', data=form(email='long' + DOMAIN, first_name='A' * 51))
    check('first name over 50 characters is rejected', r.status_code == 200 and user_count('long' + DOMAIN) == 0)

    # ---- login, session and logout ----
    c2 = app.test_client()
    r = c2.get('/bookings')
    check('protected page redirects an anonymous visitor to login', r.status_code == 302 and '/login' in r.headers['Location'])

    r = c2.post('/login', data={'email': 'valid' + DOMAIN, 'password': 'goodpass1'})
    check('newly registered user can log in', r.status_code == 302)
    check('session persists: protected page loads after login', c2.get('/bookings').status_code == 200)
    check('session persists across several requests', c2.get('/').status_code == 200 and c2.get('/bookings').status_code == 200)
    check('logged-in user visiting /register is sent home', c2.get('/register').status_code == 302)

    r = c2.get('/logout')
    check('logout redirects', r.status_code == 302)
    r = c2.get('/bookings')
    check('after logout the protected page needs a login again', r.status_code == 302 and '/login' in r.headers['Location'])

    r = app.test_client().post('/login', data={'email': 'valid' + DOMAIN.upper(), 'password': 'goodpass1'})
    check('login accepts the email in any letter case', r.status_code == 302)
    r = app.test_client().post('/login', data={'email': 'valid' + DOMAIN, 'password': 'wrongpass'})
    check('wrong password is rejected with a message', r.status_code == 200 and b'Incorrect email or password' in r.data)
    r = app.test_client().post('/login', data={'email': 'nobody' + DOMAIN, 'password': 'goodpass1'})
    check('unknown email gets the same message (no account hints)', r.status_code == 200 and b'Incorrect email or password' in r.data)
finally:
    cleanup()

print()
print('ALL PASSED' if not failures else f'{len(failures)} FAILED: {failures}')
sys.exit(1 if failures else 0)
