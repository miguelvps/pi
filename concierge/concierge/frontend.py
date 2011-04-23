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

def match_search_to_methods_keywords(query, methods):
    '''assumes word separated by single space.
    returns list of pairs of (query, method)'''
    print "query", query
    queries_methods=[]
    for method in methods:
        splited_query= query.split(' ')
        for keyword in method.resource.keywords:
            try:
                i= splited_query.index(keyword)
                method_query_splitted= splited_query[:]
                method_query_splitted.pop(i)
                method_query= " ".join(method_query_splitted)
                queries_methods.append( (method_query, method) )
            except:
                pass    #no match
    return queries_methods
    
@frontend.route('/search/')
def search():
    services= Service.query.all()
    services_urls= [s.url for s in services]
    metadatas= map(ServiceMetadata, services_urls)
    search_methods= [m.global_search() for m in metadatas]
    tmp= match_search_to_methods_keywords('professores birra', search_methods)
    print tmp
    return render_template('search.html')
