from flask import Flask

from .routes.admin import admin_bp
from .extensions import db, migrate, login_manager, assets
from .config import Config
from .routes.user import user
from .routes.zakaz import order


def create_app(confing_class=Config):
    app = Flask(__name__)
    app.config.from_object(confing_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    assets.init_app(app)

    app.register_blueprint(user)
    app.register_blueprint(order)
    app.register_blueprint(admin_bp)


    #LOGIN MANAGER
    login_manager.login_view = 'user.login'
    login_manager.login_message = 'Вы не можете получить доступ к этой странице. Нужно сначала войти!'
    login_manager.login_message_category = 'info'



    with app.app_context():
        db.create_all()


    return app

app = create_app()

