import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5

# db and login_manager are created here (not attached to an app yet)
# so that models.py and views.py can import them without circular imports.
db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'change-this-to-something-random-before-deploying'
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'fridaynight.db')
    app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'img')

    db.init_app(app)
    Bootstrap5(app)

    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'

    # models must be imported after db.init_app so the tables are registered
    from . import models

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))

    # register the routes
    from .views import main
    app.register_blueprint(main)

    # error handlers - required by the assessment brief (404 and 500)
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    # create tables if they don't exist yet (useful in dev; the submitted
    # zip should still include a pre-populated .db file per the brief)
    with app.app_context():
        db.create_all()

    return app
