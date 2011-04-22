DEBUG = True
TESTING = False
SECRET_KEY = 'secret_key'

SQLALCHEMY_DATABASE_URI = 'sqlite:///concierge.db'

CSRF_ENABLED = False

DEBUG_TB_INTERCEPT_REDIRECTS = True
DEBUG_TB_PANELS = (
    'flaskext.debugtoolbar.panels.versions.VersionDebugPanel',
    'flaskext.debugtoolbar.panels.timer.TimerDebugPanel',
    'flaskext.debugtoolbar.panels.headers.HeaderDebugPanel',
    'flaskext.debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
    'flaskext.debugtoolbar.panels.template.TemplateDebugPanel',
    'flaskext.debugtoolbar.panels.sqlalchemy.SQLAlchemyDebugPanel',
    'flaskext.debugtoolbar.panels.logger.LoggingPanel',
    'flaskext.debugtoolbar.panels.profiler.ProfilerDebugPanel',
)
