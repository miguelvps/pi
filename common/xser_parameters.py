import inspect
from xser_property import has_xser_prop, get_xser_prop
from xml_types import LIST_TYPE
from xml_types import TYPE_PROP_NAME
from xml_kinds import KIND_PROP_NAME
from xml_names import NAME_PROP_NAME
import sqlalchemy

def descends(class1, parent_class):
    return inspect.isclass(class1) and parent_class in inspect.getmro(class1)


def aux_atributes(atr_list, class_obj):
    '''gets the given atributes from the class object, if they exist'''
    d={}
    for x in (atr_list):
        v= get_xser_prop( class_obj, x, None)
        if v:
            d[x]= v
    return d

def atribute_xml_filter(atr):
    is_type= has_xser_prop(atr.atr_class, TYPE_PROP_NAME)       #is a xml_kind
    is_model_list= atr.is_model_list()     #is a list of models (relationship)
    return is_type or is_model_list

def atribute_xml_tagname(atr):
    return "entity"

def atribute_xml_atributes(atr):
    d= aux_atributes((TYPE_PROP_NAME, KIND_PROP_NAME, NAME_PROP_NAME), atr.atr_class)
    if d.get(NAME_PROP_NAME)!=None:
        #name is a function of the model or atribute
        d[NAME_PROP_NAME] = d[NAME_PROP_NAME](atr)
    return d

def atribute_xml_show_itself(atr):
    return True
def atribute_xml_show_children(atr):
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
    
def model_xml_show_itself(model):
    is_kind= has_xser_prop(model.model_class, 'kind')       #is a xml_kind
    return is_kind
def model_xml_show_children(model):
    return True




def list_xml_filter(model_list):
    return len(model_list)>0
def list_xml_tagname(model_list) :
    return 'entity'
def list_xml_atributes(model_list):
    return {'type': "list"}
def list_xml_show_itself(model_list):
    #this lines makes a list (header) only appear if it's children models are kinds
    children_are_kinds= has_xser_prop(model_list[0], 'kind')
    return len(model_list)>0 and children_are_kinds
def list_xml_show_children(model_list):
    return True

def get_serializer_parameters_for(parameters, mal):
    p= parameters[mal]
    return p['filter'], p['tagname'], p['atributes'], p['show_itself'], p['show_children']

'''
let MAL be an Model, Atribute or List (of models)

serializer_parameters is a dictionary of 3 dictionaries.

model: model parameters
atribute: dictionary of model parameters
list: the dictionary of parameters

each of these dictionaries has 5 key-value pairs:

filter:     function that specifies if the MAL and it's atributes are processed
tagname:    specifies the MAL xml tagname
atributes:   specifies the MAL xml atributes
show_itself: specifies if the MAL itself appears in the xml (may be only it's children)
show_children: specifies if the MAL's children appear in the xml 
'''


SERIALIZER_PARAMETERS= \
{
'model':
    {
    'filter':   model_xml_filter,
    'tagname':  model_xml_tagname,
    'atributes':model_xml_atributes,
    'show_itself':     model_xml_show_itself,
    'show_children' : model_xml_show_children,
    },
'atribute':
    {
    'filter':     atribute_xml_filter,
    'tagname':    atribute_xml_tagname,
    'atributes':  atribute_xml_atributes,
    'show_itself':       atribute_xml_show_itself,
    'show_children' : atribute_xml_show_children,
    },
'list':
    {
    'filter':     list_xml_filter,
    'tagname':    list_xml_tagname,
    'atributes':  list_xml_atributes,
    'show_itself':       list_xml_show_itself,
    'show_children' : list_xml_show_children,
    },
'show_empty_atributes':False
}
