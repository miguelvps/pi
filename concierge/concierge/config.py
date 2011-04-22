DEBUG = True
TESTING = False
SECRET_KEY = 'k,\xa3u\xa7;c\x1c\x9f\xc5"2\x8esF:\xb0F\xa6A?\x9bXC'

SQLALCHEMY_DATABASE_URI = 'sqlite:///concierge.db'

CSRF_ENABLED = False

DEBUG_TB_INTERCEPT_REDIRECTS = True
DEBUG_TB_PANELS = (
    'flaskext.debugtoolbar.panels.versions.VersionDebugPanel',
    'flaskext.debugtoolbar.panels.timer.TimerDebugPanel',
    'flaskext.debugtoolbar.panels.headers.HeaderDebugPanel',
    'flaskext.debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
    'flaskext.debugtoolbar.panels.template.TemplateDebugPanel',
    #'flaskext.debugtoolbar.panels.sqlalchemy.SQLAlchemyDebugPanel',
    'flaskext.debugtoolbar.panels.logger.LoggingPanel',
    'flaskext.debugtoolbar.panels.profiler.ProfilerDebugPanel',
)
