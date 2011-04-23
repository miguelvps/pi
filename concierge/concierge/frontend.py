from flask import Module, render_template
from concierge.services import Service
from concierge.service_metadata_parser import ServiceMetadata


frontend = Module(__name__, 'frontend')


@frontend.route('/')
def index():
    services = Service.query.all()
    return render_template('index.html', services = services)

    

@frontend.route('/history/')
def history():
    return render_template('history.html')


@frontend.route('/settings/')
def settings():
    return render_template('settings.html')

@frontend.route('/search/')
def search():
    services= Service.query.all()
    print "services", services
    metadatas= map(ServiceMetadata, services)
    print metadatas
    print [m.global_search() for m in metadatas]
    return render_template('search.html')
