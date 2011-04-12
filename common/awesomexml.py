class AwesomeXml:
	def __init__(self, tagname, attributes={}, content=None):
		self.name= tagname
		self.attributes= attributes
		self.subelements= []
		self.content= str(content) if content else None
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
		if tagname==None:
			return None
		if self.content:
			raise Exception("Can't append a child to a node with content")
		if type(tagname)==type(self):
			el= tagname
		else:
			el= AwesomeXml(tagname, attributes)
		self.subelements.append(el)
		return el

	def toxml(self):
		attributes= " ".join(['%s="%s"'%(k,v) for k,v in self.attributes.items()])
		start= "<%s %s>"%(self.name, attributes) if attributes else "<%s>"%(self.name)
		if self.content:
			content= self.content
		else:
			content= "".join([el.toxml() for el in self.subelements])
		
		end= "</%s>"%(self.name)
		return start+conten+tend

	def toprettyxml(self, prefix='', indentor='  '):
		attributes= " ".join(['%s="%s"'%(k,v) for k,v in self.attributes.items()])
		start= prefix+"<%s %s>\n"%(self.name, attributes) if attributes else prefix+"<%s>\n"%(self.name)
		if self.content:
			content= self.content
		else:
			content= prefix.join([el.toprettyxml(prefix+indentor, indentor) for el in self.subelements])
		end= prefix+"</%s>\n"%(self.name)
		return start+content+end
