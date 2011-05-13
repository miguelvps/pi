import inspect
from xml_kinds import xml_kind, get_model_kind
from xml_types import LIST_TYPE
import sqlalchemy

def descends(class1, parent_class):
    return inspect.isclass(class1) and parent_class in inspect.getmro(class1)

def atribute_xml_filter(atr):
  is_kind= descends(atr.atr_class, xml_kind)        #is a xml_kind
  is_model_list= atr.is_model_list()     #is a list of models (relationship)
  is_empty= (atr.atr_obj==None) or (is_model_list and len(atr.atr_obj)==0)  #value is null, or model list is empty
  return not is_empty and (is_kind or is_model_list)

def atribute_xml_tagname(atr):
  return "entity"

def atribute_xml_atributes(atr):
  k= atr.atr_class.__name__
  if hasattr(atr.atr_class, 'type'):
    return {'kind': k, 'type': atr.atr_class.type}
  else:
    return {'kind': k, 'type': "INTERNAL_DB_VALUE"}

def atribute_xml_show(atr):
    return True

  
def model_xml_filter(model):
  return True
def model_xml_tagname(model):
  return "entity"
def model_xml_atributes(model):
    kind= get_model_kind(model.model_class)
    return {'kind': kind.__name__, 'type': kind.type}
def model_xml_show(model):
    return True

def list_xml_filter(model_list):
  return True
def list_xml_tagname(model_list) :
  return 'entity'
def list_xml_atributes(model_list):
  return {'type': "list"}
def list_xml_show(atr):
    return True

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
}
