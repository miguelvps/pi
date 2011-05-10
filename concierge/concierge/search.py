
from flask import Module, render_template, request, Response, session, redirect
from concierge.services_models import Service

from concierge.service_metadata_parser import ServiceMetadata, ServiceMetadataResourceMethod

from concierge.auth import HistoryEntry
from concierge import db

from flaskext.wtf import Form, Required, Length
from flaskext.wtf.html5 import SearchField

from xml.etree import ElementTree
from common import xml_types, rest_method_parameters
from common.search import match_keywords_to_something


search = Module(__name__, 'search')


class SearchForm(Form):
    search_query = SearchField('query', validators=[Required(), Length(min=1)])

def match_search_to_methods_keywords(query, methods):
    '''assumes word separated by single space.
    returns list of pairs of (query, method)'''
    keywords_methods=[([k.keyword for k in method.resource.keywords], method) for method in methods]
    return match_keywords_to_something(query, keywords_methods)


def result_xml_to_text(xml, header=True):
    if type(xml)==str or type(xml)==unicode:
        #this is xml in string format
        xml= ElementTree.fromstring(xml.encode('utf-8'))
        
    if xml.get('type')== xml_types.LIST_TYPE:
        html_children= "".join(map(result_xml_to_text, xml.getchildren()) )
        header_html= '<h3>%s</h3>' % (xml.get('kind') or "List") if header else ''
        return '<div data-role="collapsible" data-collapsed="false" >%s%s</div>' % (header_html,html_children)
    else:
        return '<div data-role="collapsible" data-collapsed="false" ><h3>%s</h3><p>%s</p></div>' % (xml.get('kind') or "attribute", xml.text)

           

@search.route('/search/<search_query>')
def search_history(search_query):
    query = search_query #history search
    return search_aux(query)

@search.route('/search/', methods=['POST'])
def search_view():
    form = SearchForm(request.form)

    if  form.validate_on_submit():
        query= form.search_query.data

        #creates the entry in the user_history if the user is logged in
        if session.get('auth'):
            hstr_entry = HistoryEntry(user_id=session['id'], query=query)
            db.session.add(hstr_entry)
            db.session.commit()

        return search_aux(query)
    return redirect('/')   #null string case

def search_aux(query):

    services= Service.query.all()
    services_urls= [s.url for s in services]
    metadatas= map(ServiceMetadata, services_urls)
    search_methods= [m.global_search() for m in metadatas]
    matches = match_search_to_methods_keywords(query, search_methods)
    if len(matches)==0:
        #no keywords match
        results_xml=[]
    else:
        results_xml= [method.execute(query= query) for query, method in matches]
    search_results= "".join(map(result_xml_to_text, results_xml))
    return render_template('search.html', search_results=search_results)
