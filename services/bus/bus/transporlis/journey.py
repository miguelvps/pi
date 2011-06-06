import datetime

class Coordinate(object):
    def __init__(self, x,y):
        self.x, self.y= float(x), float(y)

class Journey(object):
    def __init__(self, description, start_time, end_time, wait_time, cost, operator, operator_type):
        assert type(start_time) == type(end_time)  == datetime.datetime
        assert type(wait_time) == datetime.time
        self.start_time=    start_time
        self.end_time=      end_time
        self.wait_time=     wait_time
        self.cost=          float(cost)
        self.operator=      str(operator)
        self.operator_type= str(operator_type)
        self.description=   str(description)
        


def parse_coordinate_list(magic_text):
    assert magic_text[-1]=='$'  
    cs= [xy.split(' ') for xy in magic_text.split('$')] 
    cs.pop()    #last element is empty, since sequence ends in $
    coords= [Coordinate(c[0], c[1]) for c in cs]
    return coords

def parse_journey(magic_text):
    def parse_datetime(datestr):
        return datetime.datetime.strptime(datestr, "%d-%m-%Y %H:%M:%S")
    def parse_time(datestr):
        return datetime.datetime.strptime(datestr, "%H:%M:%S").time()
    assert magic_text[-8:]=="noCoords"
    start, unknown1, description, unknown2, end, operator, cost, \
        operator_type, duration, wait, nocoords= magic_text.split("|")
    start, end= map(parse_datetime, (start, end))
    duration, wait= map(parse_time, (duration, wait))
    cost= float(cost.replace(",","."))
    assert nocoords== "noCoords"
    return Journey(description, start, end, wait, cost, operator, operator_type)
    

def get_magic_text(page):
    i= page.index("#---#")
    return page[i:]

def parse_magic_text(magic_text):
    result=[]
    while len(magic_text)>0 and magic_text[0]=='#':
        di= magic_text.index('#', 1) +1
        try:
            ci= magic_text.index('#', di)
        except:
            #end of document?
            ci=len(magic_text)-1 # -1 for \n
        
        delimiter= magic_text[0:di]
        content= magic_text[di:ci]
        result.append(  (delimiter,content)  )
        magic_text= magic_text[ci:]
    return result



    
from xml.etree import ElementTree
page= open("rota.xml").read()
mt= get_magic_text(page)
parsed= parse_magic_text(mt)



print parse_journey(parsed[20][1])
