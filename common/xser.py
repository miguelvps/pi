import sqlalchemy
import flaskext
from awesomexml import AwesomeXml
import inspect
from xser_parameters import get_serializer_parameters_for


ALLOWED_ATRIBUTE_TYPES= [sqlalchemy.types.Date, sqlalchemy.types.String]

class ModelList_xml(object):
	def __init__(self, l):
		assert hasattr(l, '__iter__')
		self.l=l
	
	def to_xml(self, parameters):
		f, t, a, s= get_serializer_parameters_for(parameters, 'list')
		if f(self):
			models_xml=[Model_Serializer(model).to_xml(parameters) for model in self.l]
			models_xml= filter(lambda a: a!=None, models_xml)
			return AwesomeXml( t(self), a(self) ).appendChild(models_xml) if s(self) else models_xml
		return None
	
	def __len__(self):
		return self.l.__len__()
	
	def __getitem__(self, i):
		return self.l.__getitem__(i)

class Model_Atribute_Serializer(object):
	TRUE_ATRIBUTE, MODEL_LIST_ATRIBUTE= range(2)
	def __init__(self, model_obj, atr_name):
		self.atr_name= atr_name
		self.atr_obj=  getattr(model_obj, atr_name)
		class_proxy= getattr( model_obj.__class__, atr_name)
		self.atr_type, self.atr_class= Model_Atribute_Serializer.extract_class_type( class_proxy)

	@staticmethod
	def extract_class_type(class_proxy):
		MAS= Model_Atribute_Serializer
		props= class_proxy.property
		if type(props) == sqlalchemy.orm.properties.ColumnProperty:
			#atribute is a "true" atribute (has a representation on the model's table)
			return (MAS.TRUE_ATRIBUTE, props.columns[0].type.__class__)
		elif type(props) == sqlalchemy.orm.properties.RelationshipProperty:
			#atribute is a relationship with other model...
			return (MAS.MODEL_LIST_ATRIBUTE, None)
		else:
			raise Exception("Found a unexpected Property type")
	
	def is_true_atribute(self):
		return self.atr_type == self.TRUE_ATRIBUTE

	def is_model_list(self):
		return self.atr_type == self.MODEL_LIST_ATRIBUTE

	def to_xml(self, parameters):
		f, t, a, s= get_serializer_parameters_for(parameters, 'atribute')
		if f(self):
			if self.is_true_atribute():
				if self.atr_obj or parameters['show_empty_atributes']:
					return AwesomeXml( t(self), a(self), self.atr_obj )
			else:
				#model list or a model object
				if hasattr(self.atr_obj, '__iter__'):
					return ModelList_xml(self.atr_obj).to_xml(parameters)
				else:
					#model object
					return Model_Serializer(self.atr_obj).to_xml(parameters)
		return None





class Model_Serializer(object):
	def __init__(self, model_obj):
		assert isinstance(model_obj, flaskext.sqlalchemy.Model)
		self.model_obj= model_obj
		self.model_class= model_obj.__class__

		atribute_names= filter(lambda k: not k[0]=='_', vars(model_obj).keys())
		self.atributes= [Model_Atribute_Serializer(model_obj, name) for name in atribute_names]

	def to_xml(self, parameters):
		f, t, a, s= get_serializer_parameters_for(parameters, 'model')
		if f(self):
			atrs_xml=[atr.to_xml(parameters) for atr in self.atributes]
			atrs_xml= filter(lambda a:a!=None, atrs_xml)
			return AwesomeXml( t(self), a(self) ).appendChild(atrs_xml) if s(self) else atrs_xml
		return None
