import inspect
from xser_property import has_xser_prop, get_xser_prop
from xml_types import LIST_TYPE
import sqlalchemy

def descends(class1, parent_class):
    return inspect.isclass(class1) and parent_class in inspect.getmro(class1)

def atribute_xml_filter(atr):
    is_kind= has_xser_prop(atr.atr_class, 'kind')       #is a xml_kind
    is_model_list= atr.is_model_list()     #is a list of models (relationship)
    return is_kind or is_model_list

def atribute_xml_tagname(atr):
    return "entity"

def atribute_xml_atributes(atr):
    k= get_xser_prop( atr.atr_class, 'kind', None)
    t= get_xser_prop( atr.atr_class, 'type', None)
    if k:
        return {'kind': k, 'type': t}
    else:
        return {}

def atribute_xml_show(atr):
    return True



  
def model_xml_filter(model):
    return True
    
def model_xml_tagname(model):
    return "entity"
    
def model_xml_atributes(model):
    d={}
    for x in ('kind', 'type'):
        v= get_xser_prop( model.model_class, x, None)
        if v:
            d[x]= v
            
    r_f= get_xser_prop( model.model_class, 'representative', None)
    if r_f:
        r= r_f(model)
        d['representative']=r
    
    return d
    
def model_xml_show(model):
    is_kind= has_xser_prop(model.model_class, 'kind')       #is a xml_kind
    return is_kind




def list_xml_filter(model_list):
    return len(model_list)>0
def list_xml_tagname(model_list) :
    return 'entity'
def list_xml_atributes(model_list):
    return {'type': "list"}
def list_xml_show(model_list):
    #this lines makes a list (header) only appear if it's children models are kinds
    children_are_kinds= has_xser_prop(model_list[0], 'kind')
    return len(model_list)>0 and children_are_kinds


def get_serializer_parameters_for(parameters, mal):
    p= parameters[mal]
    return p['filter'], p['tagname'], p['atributes'], p['show']

'''
let MAL be an Model, Atribute or List (of models)

serializer_parameters is a dictionary of 3 dictionaries.

model: model parameters
atribute: dictionary of model parameters
list: the dictionary of parameters

each of these dictionaries has 4 key-value pairs:

filter:     function that specifies if the MAL and it's atributes are processed
tagname:    function that specifies the MAL xml tagname
atributes:   function that specifies the MAL xml atributes
show:       function that specifies if the MAL itself appears in the xml, or only it's subelements
'''


SERIALIZER_PARAMETERS= \
{
'model':
    {
    'filter':   model_xml_filter,
    'tagname':  model_xml_tagname,
    'atributes':model_xml_atributes,
    'show':     model_xml_show,
    },
'atribute':
    {
    'filter':     atribute_xml_filter,
    'tagname':    atribute_xml_tagname,
    'atributes':  atribute_xml_atributes,
    'show':       atribute_xml_show,
    },
'list':
    {
    'filter':     list_xml_filter,
    'tagname':    list_xml_tagname,
    'atributes':  list_xml_atributes,
    'show':       list_xml_show,
    },
'show_empty_atributes':False
}
