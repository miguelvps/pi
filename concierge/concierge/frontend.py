from flask import Module, render_template
from concierge.services import Service


frontend = Module(__name__, 'frontend')


@frontend.route('/')
def index():
    services = Service.query.all()
    return render_template('index.html', services = services)


@frontend.route('/historico/')
def historico():
    return render_template('historico.html')


@frontend.route('/login/')
def login():
    return render_template('login.html')


@frontend.route('/service/')
def service():
    return render_template('service.html')
