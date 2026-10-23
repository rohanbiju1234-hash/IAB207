"""Checks for the SECRET_KEY and login redirect changes.
Run with: python3 -I test_login_fixes.py <path to project folder containing main.py>
"""
import os
import sys

project = sys.argv[1]
sys.path.insert(0, project)

from fridaynight import create_app  # noqa: E402

failures = []


def check(name, condition):
    print(('PASS  ' if condition else 'FAIL  ') + name)
    if not condition:
        failures.append(name)


app = create_app()
app.config['WTF_CSRF_ENABLED'] = False   # test client does not fetch CSRF tokens

# ---- SECRET_KEY ----
check('SECRET_KEY is no longer the placeholder',
      app.config['SECRET_KEY'] != 'change-this-to-something-random-before-deploying')
check('SECRET_KEY is long enough (>= 32 chars)', len(app.config['SECRET_KEY']) >= 32)

os.environ['SECRET_KEY'] = 'from-environment-variable-for-test-0123456789'
app_env = create_app()
check('SECRET_KEY environment variable overrides the fallback',
      app_env.config['SECRET_KEY'] == 'from-environment-variable-for-test-0123456789')
del os.environ['SECRET_KEY']


# ---- login redirect ----
def login_with_next(next_value):
    client = app.test_client()
    url = '/login' if next_value is None else '/login?next=' + next_value
    resp = client.post(url, data={'email': 'michael@example.com', 'password': 'password123'})
    return resp


r = login_with_next('/bookings')
check('safe next=/bookings is followed', r.status_code == 302 and r.headers['Location'] == '/bookings')

r = login_with_next('/my-events')
check('safe next=/my-events is followed', r.status_code == 302 and r.headers['Location'] == '/my-events')

for bad in ['https://evil.example', 'http://evil.example/x', '//evil.example', '/\\evil.example',
            'javascript:alert(1)']:
    r = login_with_next(bad)
    loc = r.headers.get('Location', '')
    check(f'unsafe next={bad!r} is ignored (redirects to home)', r.status_code == 302 and loc == '/')

r = login_with_next(None)
check('no next parameter goes to home', r.status_code == 302 and r.headers['Location'] == '/')

# ---- wrong password still rejected ----
client = app.test_client()
r = client.post('/login', data={'email': 'michael@example.com', 'password': 'wrong-password'})
check('wrong password does not log in', r.status_code == 200 and b'Incorrect email or password' in r.data)

print()
print('ALL PASSED' if not failures else f'{len(failures)} FAILED: {failures}')
sys.exit(1 if failures else 0)
