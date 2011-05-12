class AwesomeXml:
	def __init__(self, tagname, attributes={}, content=None):
		self.name= tagname
		self.attributes= attributes
		self.subelements= []
		self.content= unicode(content) if content else None
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
			pass
		elif self.content:
			raise Exception("Can't append a child to a node with content")
		elif type(tagname)==type(self):
			#this is an AwesomeXml, append it directly
			self.subelements.append(tagname)
		elif type(tagname)==type([]):
			#this is a list of AwesomeXml (or list of lists, etc). append all of them
			map(self.appendChild, tagname)
		else:
			#this is a tagname and attributes, create a AwesomeXml and append it
			elf.subelements.append( AwesomeXml(tagname, attributes) )
		return self

	def toxml(self):
		attributes= " ".join(['%s="%s"'%(k,v) for k,v in self.attributes.items()])
		start= "<%s %s>"%(self.name, attributes) if attributes else "<%s>"%(self.name)
		if self.content:
			content= self.content
		else:
			content= "".join([el.toxml() for el in self.subelements])
		
		end= "</%s>"%(self.name)
		return start+content+end

	def toprettyxml(self, prefix='', indentor='  '):
		attributes= " ".join(['%s="%s"'%(k,v) for k,v in self.attributes.items()])
		start= prefix+"<%s %s>"%(self.name, attributes) if attributes else prefix+"<%s>"%(self.name)
		if self.content:
			content= self.content
		else:
			start+="\n"
			content= prefix.join([el.toprettyxml(prefix+indentor, indentor) for el in self.subelements])
		if self.content:
			end= "</%s>\n"%(self.name)
		else:
			end= prefix+"</%s>\n"%(self.name)
		return start+content+end
