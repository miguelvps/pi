from flask import Module, request, session, render_template, redirect, g
from concierge.services_models import Service
from concierge import xml_to_html

from concierge.auth import HistoryEntry
from concierge import db

from flaskext.wtf import Form, Required, Length, BooleanField
from flaskext.wtf.html5 import SearchField


from common import rest_method_parameters
from common.search import match_keywords_to_something


search = Module(__name__, 'search')

class SearchForm(Form):
    search_query = SearchField('query', validators=[Required(), Length(min=1)])
    
def match_search_to_methods_keywords(query, methods):
    '''assumes word separated by single space.
    returns list of pairs of (query, method)'''
    keywords_methods=[([k.keyword for k in method.resource.keywords], method) for method in methods]
    return match_keywords_to_something(query, keywords_methods)

def add_search_to_history(query):
    #creates the entry in the user_history if the user is logged in
    if session.get('auth'):
        hstr_entry = HistoryEntry(user_id=session['id'], query=query)
        db.session.add(hstr_entry)
        db.session.commit()

@search.route('/custom_search/', methods=['GET', 'POST'])
def custom_search():
    services = Service.query.all()

    class CustomSearchForm(Form):
        search_query = SearchField('Search', validators=[Required(), Length(min=1)])
        variables = locals()
        for service in services:
            variables[service.name] = BooleanField(service.name)
        
    form = CustomSearchForm(request.form)
    services_names = [ service.name for service in services]
    service_dict = dict(zip(services_names, services))
    
    if form.validate_on_submit():
        query= form.search_query.data
        received_names = [ entry.label.text for entry in form \
                            if entry != form.search_query and entry != form.csrf and entry.data]
        received_services = [ service_dict[name] for name in received_names ]    
        return search_aux(query, received_services)  
    else:
        favorite_check = request.args.get('check_favorites', '')   # 
        if favorite_check:
            user = g.user
            favorites = user.favorite_services
            favorite_services_names = [ service.name for service in favorites ]
            for field in form:
                if field != form.search_query:
                    if field.name in favorite_services_names:
                        field.data = True
        return render_template('custom_search.html', search_form=form)

@search.route('/search/<search_query>')
def search_history(search_query):
    '''history search'''
    return search_aux( search_query , add_to_history=False)


@search.route('/search', methods=['POST'])
def search_view():
    '''general search on all services'''
    form = SearchForm(request.form)
    if  form.validate_on_submit():
        return search_aux( form.search_query.data )
    return redirect('/')   #null string case

def search_aux(query, services=None, add_to_history=True):
    '''give a list of services, and a query, executes the search on
    those services. If the list is None, search on all services.
    add_to_history is a boolean that indicates if this search should be
    added to the user search history'''
    if services==None:
        services= Service.query.all()
    if add_to_history:
        add_search_to_history(query)
    search_methods= [m.global_search() for m in services]
    matches = match_search_to_methods_keywords(query, search_methods)
    if len(matches)==0:
        #no keywords match
        results_xml=[]
    else:
        results_xml= [method.execute({rest_method_parameters.QUERY: query}) for ignoreme, method in matches]
    return xml_to_html.render_xml_list(results_xml)
