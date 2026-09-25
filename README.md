# FridayNight — Event Management System (IAB207 Assignment 2 starter)

Converted from the Assignment 1 static HTML prototype into a working Flask app.

## Run it locally

```bash
pip install -r requirements.txt
python seed_data.py     # wipes and re-creates fridaynight.db with sample data
python main.py           # starts the dev server at http://127.0.0.1:5000
```

Test logins (created by seed_data.py):
- michael@example.com / password123
- sara@example.com / password123

## What's implemented

- Landing page: browse events, category filter, keyword + AI-ranked search
- Event details: full info, comments (logged-in users), booking (logged-in users)
- Create / edit / cancel events (owner only; status can't be hand-edited per the brief)
- "My events" and "My bookings" pages
- Register / login / logout with hashed passwords (werkzeug)
- Acknowledgement of Country: none / generic / enhanced, plus an educational info page
- 404 and 500 error pages
- Database: users, events, bookings, comments (4 required tables)

## What YOUR TEAM still needs to do before submitting

1. **Real AI-enhanced search** (`fridaynight/ai_search.py`) — the current version is a
   difflib placeholder so the app runs with no extra installs. Swap it for real
   sentence-transformers embeddings (see the docstring in that file for the exact
   code) or confirm a different approved AI approach with your tutor.
2. **Style/rebrand** if you want to move away from "FridayNight" — just find/replace.
3. **More sample data** — add more events/users/bookings so the deployed site looks
   populated (the brief wants "a good sample" with varied statuses).
4. **Team review of the Acknowledgement of Country feature** — the enhanced option
   currently lets the creator free-type custodians + statement. Read the brief's
   rubric again as a team and consider adding more guided prompts/checks for full marks.
5. **Deploy to PythonAnywhere** and put the link in your Declaration document.
6. **Rename folder** from `a2_group0` to your real Canvas group number before zipping.
7. **Update SECRET_KEY** in `fridaynight/__init__.py` to something random before deploying.
8. Write your Assignment Declaration document (team details, individual contributions, AI use disclosure).

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
    ai_search.py              <- AI-enhanced discovery (upgrade this!)
    fridaynight.db             <- created after you run seed_data.py
    templates/
    static/
```
