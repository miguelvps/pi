from flask import Flask, request, g
from flaskext.babel import Babel
from flaskext.sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app(cfg=None):
    app = Flask(__name__)

    app.config.from_object('concierge.config')
    app.config.from_envvar('CONCIERGE_SETTINGS', silent=True)
    if cfg: app.config.from_object(cfg)

    db.init_app(app)

    babel = Babel(app)

    @babel.localeselector
    def get_locale():
        user = getattr(g, 'user', None)
        if user is not None and user.locale:
            return user.locale
        return request.accept_languages.best_match(['pt', 'en'])

    if app.config['DEBUG_TB_ENABLED']:
        from flaskext.debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension(app)

    from concierge.frontend import frontend
    app.register_module(frontend)

    from concierge.search import search
    app.register_module(search)

    from concierge.auth import auth
    app.register_module(auth, url_prefix='/auth')

    from concierge.services_models import services_models
    app.register_module(services_models)

    from concierge.services import services
    app.register_module(services, url_prefix='/services')

    from concierge.api import api
    app.register_module(api, url_prefix='/api')

    return app
