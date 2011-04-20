from flask import Flask, render_template
from flaskext.sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config.from_object('concierge.config')
try: app.config.from_envvar('CONCIERGE_SETTINGS')
except: pass

db = SQLAlchemy(app)


from concierge.auth import auth
app.register_module(auth, url_prefix='/auth')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/historico/')
def historico():
    return render_template('historico.html')


@app.route('/login/')
def login():
    return render_template('login.html')


@app.route('/service/')
def service():
    return render_template('service.html')
