from xml.etree import ElementTree
from flask import Module, request, session, render_template, redirect, g
from concierge.services_models import Service, ResourceMethod

from concierge.auth import HistoryEntry
from concierge import db

from flaskext.wtf import Form, Required, Length, BooleanField
from flaskext.wtf.html5 import SearchField

from common import rest_method_parameters
from common.search import match_keywords_to_something
from concierge import xml_to_html


search = Module(__name__, 'search')

class SearchForm(Form):
    search_query = SearchField('query', validators=[Required(), Length(min=1)])

def match_search_to_methods_keywords(query, methods):
    '''assumes word separated by single space.
    returns list of pairs of (query, method)'''
    keywords_methods=[([k.keyword for k in method.resource.keywords], method) for method in methods]
    return match_keywords_to_something(query, keywords_methods)

def add_search_to_history(query, services):
    #creates the entry in the user_history if the user is logged in
    if session.get('auth'):
        hstr_entry = HistoryEntry(user = g.user, search_query=query, entry_services=services)
        db.session.add(hstr_entry)
        db.session.commit()
        
@search.route('/custom_search', methods=['GET', 'POST'])
def custom_search(history_entry = None, entry_id = None):
    services = Service.query.all()

    class CustomSearchForm(Form):
        search_query = SearchField('Search', validators=[Required(), Length(min=1)])
        variables = locals()
        for service in services:
            variables[service.name] = BooleanField(service.name)

    form = CustomSearchForm(request.form)
    services_names = [ service.name for service in services]
    service_dict = dict(zip(services_names, services))

    if form.validate_on_submit():   #POST form
        query= form.search_query.data
        received_names = [ entry.label.text for entry in form \
                            if entry != form.search_query and entry != form.csrf and entry.data]
        received_services = [ service_dict[name] for name in received_names ]
        return search_aux(query, received_services)

    elif history_entry != None: #History search
        selected_services = history_entry.entry_services
        selected_services_names = [ service.name for service in selected_services]
        for field in form:
            if field == form.search_query:
                form.search_query.data = history_entry.search_query
            elif field.name in selected_services_names:
                field.data = True
        return render_template('custom_search.html', search_form=form, history_call='false')

    elif entry_id != None:  #localStorage history entry id
        return render_template('custom_search.html', search_form=form, entry_id=entry_id, history_call='true')

    else:   #Favorite services button
        favorite_check = request.args.get('check_favorites', '')
        fav_check = 'false' #for localStorage favorite button press
        if favorite_check:
            fav_check = 'true'
            if hasattr(g, 'user'):
                user = g.user
                favorites = user.favorite_services
                favorite_services_names = [ service.name for service in favorites ]
                for field in form:
                    if field != form.search_query:
                        if field.name in favorite_services_names:
                            field.data = True
        return render_template('custom_search.html', search_form=form, history_call='false', fav_check=fav_check)

@search.route('/search/<entry_id>')
def search_history(entry_id):
    '''history search'''
    if hasattr(g, 'user'):
        user = g.user
        history = user.user_history
        entry = HistoryEntry.query.get_or_404(entry_id)
        return custom_search(history_entry = entry)
    return custom_search(entry_id=entry_id)

@search.route('/search', methods=['GET', 'POST'])
def search_view():
    form = SearchForm(request.form)
    if form.validate_on_submit():
        return search_aux(form.search_query.data)
    else:
        query = request.args.get('query', None)
        if query:
            return search_aux(query.encode('utf-8'), add_to_history=False)
    return redirect('/')

def search_aux(query, services=None, add_to_history=True):
    '''give a list of services, and a query, executes the search on
    those services. If the list is None, search on all services.
    add_to_history is a boolean that indicates if this search should be
    added to the user search history'''
    if services==None:
        services= Service.query.all()
    if add_to_history:
        add_search_to_history(query, services)
    search_methods= [m.global_search() for m in services]
    matches = match_search_to_methods_keywords(query, search_methods)

    params= {rest_method_parameters.QUERY: query}
    method_parameters= [(method, params) for ignoreme, method in matches]
    results= filter(lambda x:x is not None, ResourceMethod.execute_several(method_parameters))

    xml = ElementTree.Element("entity", type='list')
    for result in results:
        result_xml = ElementTree.fromstring(result)
        if result_xml.tag == 'data':
            result_xml = result_xml.getchildren()[0]
        for e in result_xml:
            xml.append(e)
            
    html= xml_to_html.render(xml)
    return render_template('search.html', html=html)
