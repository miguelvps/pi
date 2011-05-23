from flask import Module, render_template, request, g
from concierge.services_models import Service
from concierge.search import SearchForm
from concierge import db


frontend = Module(__name__, 'frontend')


@frontend.route('/')
def index():
    searchform = SearchForm(request.form)
    services = Service.query.all()
    return render_template('index.html', services = services, search_form=searchform)

@frontend.route('/history', methods=['GET', 'POST'])
def history():
    if hasattr(g, 'user'):
        user = g.user
        history = user.user_history

        if request.method =='POST': 

            for entry in history:   #clear user history
                db.session.delete(entry)
            db.session.commit()
        history = user.user_history #update object
        return render_template('history.html', history=history)

    return render_template('history.html', history=[])


@frontend.route('/settings')
def settings():
    return render_template('settings.html')

@frontend.route('/map')
def map():
    return render_template('map.html')
