import sqlalchemy
import flaskext
from awesomexml import AwesomeXml
import inspect


ALLOWED_ATRIBUTE_TYPES= [sqlalchemy.types.Date, sqlalchemy.types.String]


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
		axf, axt, axa= parameters[3:6]
		if axf(self):
			if self.is_true_atribute():
				return AwesomeXml( axt(self), axa(self), self.atr_obj )
			else:
				xml= AwesomeXml( axt(self), axa(self) )
				for model in self.atr_obj:
					xml.appendChild( Model_Serializer(model).to_xml(parameters) )
				return xml
		return None





class Model_Serializer(object):
	def __init__(self, model_obj):
		assert isinstance(model_obj, flaskext.sqlalchemy.Model)
		self.model_obj= model_obj
		self.model_class= model_obj.__class__

		atribute_names= filter(lambda k: not k[0]=='_', vars(model_obj).keys())
		self.atributes= [Model_Atribute_Serializer(model_obj, name) for name in atribute_names]

	def to_xml(self, parameters):
		mxf, mxt, mxa= parameters[0:3]
		
		if mxf(self):
			xml= AwesomeXml( mxt(self), mxa(self) )
			for atr in self.atributes:
				xml.appendChild(atr.to_xml(parameters))
			return xml
		return None
