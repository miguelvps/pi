import csv
import itertools

priority_dictionary= {'M':0, 'S':1, 'C':2, 'W':3}
type_dictionary= {'FUN':0, 'INF':1, 'INT':2, 'ARQ':3, 'SEG':4, 'ENG':5, 'TEC':6}
subsystem_dictionary= {'CLI':0, 'CON':1, 'GEO':2, 'PES':3, 'ORG':4, 'IP':5, 'BUS':6, 'BIB':7}


class Requisite():
	def __init__(self, reqlist, subsistema, tipo, prioridade, agrupamento, descricao):
		#print "creating requisite", subsistema, tipo, prioridade, agrupamento, descricao
		_= subsystem_dictionary[subsistema]
		_= type_dictionary[tipo]
		_= priority_dictionary[prioridade]
		
		self.subsystem= subsistema
		self.type= tipo
		self.priority= prioridade
		
		self.group= agrupamento
		self.description= descricao #.decode("UTF-8")
		self.id=0
		self.subid=0

	def full_id(self):
		s="%s-%s- %.3d"%(self.subsystem,self.type,self.id)
		if self.subid:
			s+="-%.2d"%(self.subid)
		return s

	def __repr__(self):
		return self.full_id()+"\t"+self.priority+"\t"+self.description
		
class RequisiteList():
	def __init__(self, csvfile):
		parser = csv.reader(open(csvfile, 'rb'), delimiter=',')
		
		rows1= [row for row in parser]
		rows1= filter(lambda t:len(t), rows1)
		rows2=[]
		for row in rows1:
			#print row
			rows2.append((self, row[1], row[2], row[3], row[4], row[5]))
		#rows2=  [(self, row[1], row[2], row[3], row[4], row[5]) for row in rows1]
		
		self.reqlist= [Requisite(*row) for row in rows2]
		

	def generate_ids(self):
		idcounter= 0
		groups= {}
		for req in self.reqlist:
			if req.group:
				if not req.group in groups:
					groups[req.group]=0
					req.id= idcounter
					idcounter+=1
				req.subid= groups[req.group]
				req.id= idcounter
				groups[req.group]+=1
			else:
				req.id= idcounter
				idcounter+=1
	
	def print_by_attribute(self, atribute_str):
		k= lambda a:getattr(a,atribute_str)
		self.reqlist.sort(key= k)
		groups= itertools.groupby(self.reqlist, k)
		for i in groups:
			print ""
			for r in i[1]:
				print r
			
	
	def printlist(self):
		for req in self.reqlist:
			print req
	
	def export_to_pivotal_tracker(self):
		print u"Story,Description"
		for req in self.reqlist:
			print "%s | %s,%s"%(req.full_id(), req.description, '')

	def full_print(self):
		print u"ID\tPrioridade\tDescricao"
		print "LISTAGEM"
		self.printlist()
		print "\n----------------\n"

		print "ORDENADOS POR SUBSISTEMA"
		self.print_by_attribute("subsystem")
		print "\n----------------\n"

		print "ORDENADOS POR TIPO"
		self.print_by_attribute("type")
		print "\n----------------\n"

		print "ORDENADOS POR PRIORIDADE"
		self.print_by_attribute("priority")
		print "\n----------------\n"


rl= RequisiteList("requisitos.csv")
rl.generate_ids()
#rl.full_print()
rl.export_to_pivotal_tracker()
