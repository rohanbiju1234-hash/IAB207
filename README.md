# FridayNight: Event Management System (IAB207 Assignment 2, Group 12)

A Flask event management site for live music nights, built from our Assignment 1 prototype.

Live site: https://tanvisharma.pythonanywhere.com

## Run it locally

From the project folder (the one containing `main.py`):

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python main.py                  # starts the dev server at http://127.0.0.1:5000
```

The submitted zip already includes a populated database (`fridaynight/fridaynight.db`), so
`python main.py` works straight after installing the requirements. To reset the sample data, run
`python seed_data.py` first (it wipes the database and recreates it).

Test logins (created by `seed_data.py`):
- michael@example.com / password123
- sara@example.com / password123
- liam@example.com / password123
- priya@example.com / password123

## What's implemented

- Landing page: browse events, category filter, Smart (AI-ranked) or Exact keyword search
- Event details: full info, comments (logged-in users), booking (logged-in users), related events
- Booking rules: over-capacity bookings are rejected, and an event becomes Sold Out when the last ticket is taken
- Create, edit and cancel events (owner only; status can't be hand-edited per the brief)
- "My events" and "My bookings" pages
- Register, login and logout with hashed passwords (werkzeug)
- Acknowledgement of Country: none, generic or enhanced (guided by a location list of Traditional Custodians), plus an educational info page
- Navigation menu on every page, and 404 and 500 error pages
- Database: users, events, bookings, comments (4 required tables)

## Deployment and search notes

- Deployed on PythonAnywhere (free account). `sentence-transformers` (the AI search library) is too
  large for the free tier, so it is commented out in `requirements.txt`. The deployed site falls back
  to keyword search, and related events fall back to same-category events.
- To run the real semantic search locally, run `pip install sentence-transformers`
  (the model downloads the first time you search).
- The sample data in `seed_data.py` covers all event statuses (Open, Inactive, Sold Out, Cancelled)
  and all categories.
- On the deployed site, set the `SECRET_KEY` environment variable. The key in
  `fridaynight/__init__.py` is only a local fallback.
- After login, the `?next=` redirect only follows paths on this site, so a crafted link cannot send
  a user to another website.

## Run the automated tests

Run `python seed_data.py` first so the login tests have the sample users, then:

```bash
python tests\test_login_fixes.py .       # SECRET_KEY and login redirect checks
python tests\test_register.py .          # registration, login, session and logout checks
python -m unittest tests.test_search     # search and related-events checks
```

## Folder structure

```
a2_group12/
  Assignment declaration
  main.py                    <- run this
  seed_data.py
  requirements.txt
  README.md
  fridaynight/               <- the Flask package
    __init__.py              <- app factory
    models.py                <- User, Event, Booking, Comment
    forms.py                 <- Flask-WTF forms
    views.py                 <- all routes
    ai_search.py             <- AI-enhanced search (keyword fallback)
    fridaynight.db           <- sample database, included in the zip
    templates/
    static/
  tests/
    test_login_fixes.py
    test_register.py
    test_search.py
```
