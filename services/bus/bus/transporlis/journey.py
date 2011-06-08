import datetime

class Coordinate(object):
    def __init__(self, x,y):
        self.x, self.y= float(x), float(y)
        self.c=(x,y)
        
    def __repr__(self):
        return str(self.c)
    def __len__(self):
        return 2
    def __getitem__(self, key):
        return self.c[key]
    def __iter__(self):
        return self.c.__iter__()

class Path(object):
    '''list of coordinates'''
    def __init__(self, l):
        assert all([isinstance(c, Coordinate) for c in l])
        self.l= l

    def __repr__(self):
        return "<Path>"
    def __len__(self):
        return len(self.l)
    def __getitem__(self, key):
        return self.l[key]
    def __iter__(self):
        return self.l.__iter__()

class BoundingBox(object):
    '''for determining zoom'''
    def __init__(self, c1,c2):
        assert isinstance(c1, Coordinate)
        assert isinstance(c2, Coordinate)
        self.l=[c1,c2]

    def center(self):
        x1,y1,x2,y2= self.c1.x, self.c1.y, self.c2.x, self.c2.y,
        return Coordinate(((x1+x2)/2),(y1+y2)/2)
        
    def __len__(self):
        return len(self.l)
    def __getitem__(self, key):
        return self.l[key]
    def __iter__(self):
        return self.l.__iter__()

class Journey(object):
    '''a list of JourneyTransport'''
    def __init__(self, list_of_transports, bounding_box):
        assert all([isinstance(t, JourneyTransport) for t in list_of_transports])
        assert isinstance(bounding_box, BoundingBox)
        self.transports= list_of_transports
        self.bounding_box= bounding_box

    def distance(self):
        return sum([t.distance for t in self.transports])
    def price(self):
        return sum([t.cost for t in self.transports])
    def co2(self):
        return sum([t.co2 for t in self.transports])
    def start_time(self):
        return self.transports[0].start_time
    def end_time(self):
        return self.transports[-1].end_time
    
        
    def __len__(self):
        return self.transports.__len__()
    def __getitem__(self, key):
        return self.transports[key]
    def __iter__(self):
        return self.transports.__iter__()





    
class JourneyTransport(object):
    '''a journey in a given transport'''
    def __init__(self, description, start_time, end_time, wait_time, cost, operator, operator_type, co2, distance):
        assert type(start_time) == type(end_time)  == datetime.datetime
        assert type(wait_time) == datetime.time
        self.start_time=    start_time
        self.end_time=      end_time
        self.wait_time=     wait_time
        self.cost=          float(cost)
        self.operator=      str(operator)
        self.operator_type= str(operator_type)
        self.description=   str(description)
        self.co2=           int(co2)
        self.distance=      int(distance)

    def set_paths(self, paths):
        '''sets the paths of various steps of thens
        transportation (stations, etc)'''
        assert all([isinstance(p, Path) for p in paths])
        self.paths= paths




def parse_path(magic_text):
    '''parses "coord coord$coord coord$"...'''
    assert magic_text[-1]=='$'  
    cs= [xy.split(' ') for xy in magic_text.split('$')] 
    cs.pop()    #last element is empty, since sequence ends in $
    coords= [Coordinate(c[0], c[1]) for c in cs]
    return Path(coords)

def parse_bounding_box(magic_text):
    '''parses "coord/coord coord/coord"...'''
    cs= [xy.split('/') for xy in magic_text.split(' ')]
    assert len(cs)==2
    coords= [Coordinate(c[0], c[1]) for c in cs]
    return BoundingBox(coords[0], coords[1])
    
def parse_journey_transport(magic_text):
    def parse_datetime(datestr):
        return datetime.datetime.strptime(datestr, "%d-%m-%Y %H:%M:%S")
    def parse_time(datestr):
        return datetime.datetime.strptime(datestr, "%H:%M:%S").time()
    assert magic_text[-8:]=="noCoords"
    start, co2, description, distance, end, operator, cost, \
        operator_type, duration, wait, nocoords= magic_text.split("|")
    wait= wait if wait!='' else "00:00:00"
    if co2[-1]=="g":
        #sometimes co2 ends with g (grams)
        co2= co2[:-1]
    start, end= map(parse_datetime, (start, end))
    duration, wait= map(parse_time, (duration, wait))
    cost= float(cost.replace(",","."))
    assert nocoords== "noCoords"
    return JourneyTransport(description, start, end, wait, cost, operator, operator_type, co2, distance)
     
def get_magic_text_from_html(html):
    i= html.index("#---#")
    text= html[i:]
    if text[-1]=="\n":
        return text[:-1]
    else:
        return text 

def magic_text_to_list(magic_text):
    '''parses magic text delimiters, returns a list of tuple in the form
    (delimiter, content_after_delimiter)'''
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




def parse(html):
    '''main function. returns a Jorney object from the html'''
    try:
        mt= get_magic_text_from_html(html)
    except:
        raise Exception("Could not find magic text in returned page. page dump:\n"+html)
    mtl= magic_text_to_list(mt)
    contents= zip(*mtl)[1]
    assert len(contents)>0

    list_of_path_list=[]
    i=-1
    while True:
        path_list=[]
        while True:
            i+=1
            if contents[i]!="":
                path= parse_path(contents[i])
                path_list.append( path )
            else:
                break
        list_of_path_list.append( path_list )
        if contents[i+1]=="":
            break
        
    i+=2
    list_of_transports=[]
    while True:
        if contents[i]!="":
            list_of_transports.append(parse_journey_transport(contents[i]))
        else:
            break
        i+=1

    assert len(list_of_path_list)==len(list_of_transports)

    bounding_box= parse_bounding_box(contents[i+1])




    for transport, paths in zip(list_of_transports, list_of_path_list):
        #associate each transport with it's paths
        transport.set_paths(paths)

    return Journey(list_of_transports, bounding_box)
