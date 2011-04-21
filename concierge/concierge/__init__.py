from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app(cfg=None):
    app = Flask(__name__)

    app.config.from_object('concierge.config')
    if cfg: app.config.from_object(cfg)
    try: app.config.from_envvar('CONCIERGE_SETTINGS')
    except: pass

    db.init_app(app)

    from concierge.frontend import frontend
    app.register_module(frontend)

    from concierge.auth import auth
    app.register_module(auth, url_prefix='/auth')

    return app