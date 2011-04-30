from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app(cfg=None):
    app = Flask(__name__)

    app.config.from_object('concierge.config')
    app.config.from_envvar('CONCIERGE_SETTINGS', silent=True)
    if cfg: app.config.from_object(cfg)

    db.init_app(app)

    if app.config['DEBUG_TB_ENABLED']:
        from flaskext.debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension(app)

    from concierge.frontend import frontend
    app.register_module(frontend)

    from concierge.search import search
    app.register_module(search)

    from concierge.services_models import services_models
    app.register_module(services_models)

    from concierge.services import services
    app.register_module(services, url_prefix='/services')

    from concierge.auth import auth
    app.register_module(auth, url_prefix='/auth')

    return app
