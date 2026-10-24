# FridayNight — Event Management System (IAB207 Assignment 2, Group 12)

A Flask event management site for live music nights, built from our Assignment 1 prototype.
Live site: https://tanvisharma.pythonanywhere.com

## Run it locally

```bash
pip install -r requirements.txt
python seed_data.py     # wipes and re-creates fridaynight.db with sample data
python main.py           # starts the dev server at http://127.0.0.1:5000
```

Test logins (created by seed_data.py):
- michael@example.com / password123
- sara@example.com / password123
- liam@example.com / password123
- priya@example.com / password123

## What's implemented

- Landing page: browse events, category filter, Smart (AI-ranked) or Exact keyword search
- Event details: full info, comments (logged-in users), booking (logged-in users), related events
- Booking rules: over-capacity bookings are rejected, and an event becomes Sold Out when the last ticket is taken
- Create / edit / cancel events (owner only; status can't be hand-edited per the brief)
- "My events" and "My bookings" pages
- Register / login / logout with hashed passwords (werkzeug)
- Acknowledgement of Country: none / generic / enhanced (guided by a location list of Traditional Custodians), plus an educational info page
- 404 and 500 error pages
- Database: users, events, bookings, comments (4 required tables)

## Deployment and search notes

- Deployed on PythonAnywhere (free account). `sentence-transformers` (the AI search library) is too
  large for the free tier, so it is commented out in `requirements.txt`. The deployed site falls back
  to keyword search, and related events fall back to same-category events.
- To run the real semantic search locally, run `pip install sentence-transformers`
  (the model downloads the first time you search).
- The sample data in `seed_data.py` covers all event statuses (Open, Inactive, Sold Out, Cancelled)
  and all categories. Running it wipes the database and recreates it.
- On the deployed site, set the `SECRET_KEY` environment variable. The key in
  `fridaynight/__init__.py` is only a local fallback.

## Folder structure

```
a2_groupX/
  main.py                  <- run this
  seed_data.py
  requirements.txt
  fridaynight/              <- your Flask package
    __init__.py             <- app factory
    models.py                <- User, Event, Booking, Comment
    forms.py                 <- Flask-WTF forms
    views.py                 <- all routes
    ai_search.py              <- AI-enhanced search (keyword fallback)
    fridaynight.db             <- created after you run seed_data.py
    templates/
    static/
```
