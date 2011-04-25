from flask import Module, render_template, request, Response
from concierge.services import Service
from concierge.search import SearchForm




frontend = Module(__name__, 'frontend')


@frontend.route('/')
def index():
    searchform = SearchForm(request.form)
    services = Service.query.all()
    return render_template('index.html', services = services, search_form=searchform)

    

@frontend.route('/history/')
def history():
    return render_template('history.html')


@frontend.route('/settings/')
def settings():
    return render_template('settings.html')

