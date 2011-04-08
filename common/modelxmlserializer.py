from awesomexml import AwesomeXml
import inspect

def model_kind(model_class, db):
	return model_class.__name__

def model_type(model_class, db):
	return "list"

def model_name(model_class, db):
	return "entity"

def atribute_type(atribute_class, db):
	assert hasattr(atribute, 'type')
	return atribute.type

def atribute_kind(atribute_class, db):
	return atribute_class.__name__

def atribute_name(atribute_class, db):
	return "entity"


def xml_atrs(kind, type):
	d= {'kind':kind, 'type':type}
	for k in d.keys():	#remove empty string atributes 
		if not d[k]:
			d.pop(k)

def xml_of_atribute(atribute_name, model_object, db):
	atribute_object= getattr(model_object, atribute_name)
	atribute_class= getattr(model_object.__class__, atribute_name).property.columns[0].type
	atribute_ancestors= inpect.getmro()
	allowed_types= [db.Date, db.String]
	assert any(map(lambda a:a==atribute_class, allowed_types))
	
	kind= atribute_kind(atribute_class, db)
	type= atribute_type(atribute_class, db)
	xml_atributes= xml_atrs(atrkind, atrtype)
	xml_name= atribute_name(atribute, db)
	return AwesomeXml(xml_name, xml_atributes)

def model_atribute_names(model_class):
	'''gives all the attributes of a model (not including implementation junk)'''
	atributes= vars(model_class)
	return filter(lambda k: not k[0]=='_', atributes.keys())

def xml_of_model(model_object, db):
	assert isinstance(model_object, db.Model)
	model_class= model_object.__class__
	
	modelname= model_name(model_class, db)
	modelkind= model_kind(model_class, db)
	modeltype= model_kind(model_class, db)
	result= AwesomeXml( modelname, xml_atrs(modelkind, modeltype) )
	
	atribute_names= model_atribute_names(model_class)
	for atr_name in atribute_names:
		result.appendChild(xml_of_atribute(atr_name, model_object,db))

	if hasattr(model_object, '_lists'):
		for atr_name in model_object._lists:
			result.appendChild(xml_of_atribute(atr_name, model_object,db))
	return result


'''type(Teacher.name.property.columns[0].type)
'''
