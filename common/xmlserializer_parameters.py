import inspect
import xml_kinds
from xml_types import LIST_TYPE
import sqlalchemy


kinds= [ x for x in vars(xml_kinds).values() if inspect.isclass(x) and sqlalchemy.types.AbstractType in inspect.getmro(x)]

def atribute_xml_filter(atr):
	is_kind= atr.atr_class in kinds			#is a xml_kind
	is_model_list= atr.is_model_list()	#is a list of models (relationship)
	is_empty= (atr.atr_obj==None) or (is_model_list and len(atr.atr_obj)==0)	#value is null, or model list is empty
	return not is_empty and (is_kind or is_model_list)
	
def atribute_xml_tagname(atr):
	return "entity"

def atribute_xml_atributes(atr):
  if atr.atr_class==None:
    return {'type': 'list'}
  else:
    k= atr.atr_class.__name__
    if hasattr(atr.atr_class, 'type'):
      return {'kind': k, 'type': atr.atr_class.type}
    else:
      return {'kind': k, 'type': "INTERNAL_DB_VALUE"}


def model_xml_filter(model):
	return True
def model_xml_tagname(model):
	return "entity"
def model_xml_atributes(model):
	return {'kind': model.model_class.__name__, 'type': LIST_TYPE}



SERIALIZER_PARAMETERS= [model_xml_filter, model_xml_tagname, model_xml_atributes, atribute_xml_filter, atribute_xml_tagname, atribute_xml_atributes]
