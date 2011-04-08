class AwesomeXml:
	def __init__(self, tagname, attributes={}):
		self.name= tagname
		self.attributes= attributes
		self.subelements= []
		self.__iter_index=0

	def __getitem__(self, key):
		return self.subelements[key]

	def __iter__(self):
		return self

	def next(self):
		if self.__iter_index>=len(self.subelements):
			raise StopIteration
		self.__iter_index+=1
		return self.subelements[self.__iter_index-1]

	def appendChild(self, tagname, attributes={}):
		if type(tagname)==type(self):
			el= tagname
		else:
			el= AwesomeXml(tagname, attributes)
		self.subelements.append(el)
		return el

	def toxml(self):
		attributes= " ".join(['%s="%s"'%(k,v) for k,v in self.attributes.items()])
		start= "<%s %s>"%(self.name, attributes) if attributes else "<%s>"%(self.name)
		subelements= "".join([el.toxml() for el in self.subelements])
		end= "</%s>"%(self.name)
		return start+subelements+end

	def toprettyxml(self, prefix='', indentor='  '):
		attributes= " ".join(['%s="%s"'%(k,v) for k,v in self.attributes.items()])
		start= prefix+"<%s %s>\n"%(self.name, attributes) if attributes else prefix+"<%s>\n"%(self.name)
		subelements= prefix.join([el.toprettyxml(prefix+indentor, indentor) for el in self.subelements])
		end= prefix+"</%s>\n"%(self.name)
		return start+subelements+end
