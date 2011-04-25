from flask import Module, render_template, request, Response
from concierge.services import Service
from concierge.service_metadata_parser import ServiceMetadata


from flaskext.wtf import Form, Required
from flaskext.wtf.html5 import SearchField


search = Module(__name__, 'search')


class SearchForm(Form):
    search_query = SearchField('query', validators=[Required()])
    
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
    
@search.route('/search/', methods=['GET','POST'])
def search_view():

    form = SearchForm(request.form)
    
    if form.validate_on_submit():
        return render_template('search.html')
        query= form.search_query
        
        services= Service.query.all()
        services_urls= [s.url for s in services]
        metadatas= map(ServiceMetadata, services_urls)
        search_methods= [m.global_search() for m in metadatas]
        
        tmp= match_search_to_methods_keywords(query, search_methods)
        #return Response(response= tmp)
        return render_template('search.html')
    return render_template('seds.html')
