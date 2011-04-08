from awesomexml import AwesomeXml

def model_kind(model_object, db):
	return model_object.__class__.__name__

def model_type(model_object, db):
	return "list"

def model_name(model_object, db):
	return "entity"

def atribute_type(atribute, db):
	f= lambda x: isinstance(atribute, x)
	allowed_types= [db.Date, db.String]
	print type(atribute)
	assert any(map(f, allowed_types))
	assert hasattr(atribute, 'type')
	return atribute.type

def atribute_kind(atribute, db):
	return atribute.__class__.__name__

def atribute_name(atribute, db):
	return "entity"


def xml_atrs(kind, type):
	d= {'kind':kind, 'type':type}
	for k in d.keys():	#remove empty string atributes 
		if not d[k]:
			d.pop(k)

def xml_of_atribute(atribute, db):
	kind= atribute_kind(atribute, db)
	type= atribute_type(atribute, db)
	xml_atributes= xml_atrs(atrkind, atrtype)
	xml_name= atribute_name(atribute, db)
	return AwesomeXml(xml_name, xml_atributes)

def xml_of_model(model_object, db):
	assert isinstance(model_object, db.Model)
	modelname= model_name(model_object, db)
	modelkind= model_kind(model_object, db)
	modeltype= model_kind(model_object, db)
	result= AwesomeXml( modelname, xml_atrs(modelkind, modeltype) )
	
	atributes= vars(model_object)
	good_atributes_names= filter(lambda k: not k[0]=='_', atributes.keys())
	for k in good_atributes_names:
		atr=atributes[k]
		result.appendChild(xml_of_atribute(atr, db))

	if hasattr(model_object, '_lists'):
		for l in [getattr(model_object, lname) for lname in model_object._lists]:
			for atr in l:
				result.appendChild(xml_of_atribute(atr, db))
	return result

