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

@frontend.route('/settings/')
def settings():
    return render_template('settings.html')

@frontend.route('/bookmark_list/')
def bookmark_list():
        return render_template('bookmark_list.html')
    

