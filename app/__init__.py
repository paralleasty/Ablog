import os
import logging
from logging.handlers import RotatingFileHandler
# from config import config
from config import DevelopmentConfig
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_migrate import Migrate


bootstrap = Bootstrap()
moment = Moment()
csrf = CSRFProtect()
db = SQLAlchemy()
pagedown = PageDown()
migrate = Migrate()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_name=DevelopmentConfig):
    # if config_name is None:
    #     config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask(__name__)
    app.config.from_object(config_name)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    pagedown.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # 避免循环依赖
    from app.main import main_bp
    app.register_blueprint(main_bp)

    from app.admin import admin_bp
    app.register_blueprint(admin_bp)

    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.errors import errors_bp
    app.register_blueprint(errors_bp)

    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # 在未调试启用日志记录
    if not app.debug:
        if not os.path.exists('log'):
                os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/blog.log',
                                           maxBytes=102400, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineo)d'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Blog startup')

    return app
