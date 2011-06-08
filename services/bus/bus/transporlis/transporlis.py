import urllib
import journey
import re

def parse_pesquisar_lugar(html):
        '''returns list of [lat, long, place_name]'''
        #print "html" , html
        if html=="Erro":
            raise Exception("remote end error")
        if not 'value=' in html:
            #a single result, no html
            tmp= html.split("/") 
            if tmp[0]!="coordenadas":
                raise Exception("remote end error")
            return [tmp[1:]]
        else:
            matches= re.findall('value="(.*?)"', html)
            matches= map(lambda m: m.split('/'), matches)
            return matches
            

def geolocate(place_string):
    method_url= 'http://transporlis.sapo.pt:80//DesktopModules/trp_homepage/Ajax/trp_homepage.ashx'
    params= {"cmd": "pesquisarLugar",
             "Lugar": place_string}
    request_params= urllib.urlencode(params)
    html = urllib.urlopen(method_url + "?" + request_params).read()
    return parse_pesquisar_lugar(html)

    


def transportation(lat1, long1, lat2, long2, journey_datetime):
    '''example: transportation(38.748893448241,-9.1445932910152,38.716755469796,-9.1693125292957, datetime.datetime.now())'''
    method_url= 'http://transporlis.sapo.pt:80/DesktopModules/trp_calculo_percurso/Ajax/trp_calculo_percurso.ashx'
    base_params=    {
                    "cmd": "recuperarRota",
                    'isKyosk': "false",
                    }
        
    #convert lat/long to strings
    lat1,long1, lat2, long2= map(str, (lat1,long1, lat2, long2))
    datarota= journey_datetime.date().strftime("%d/%m/%Y")
    horarota= journey_datetime.time().strftime("%H:%M")
    #autocarro, metro, comboio, barco
    transportes= "true,true,true,true"
    #1:mais rapido      4:menos pedonal      64:menos transbordos
    tipopercurso=1
        
    extra_params= {
                    "textPartida":      "Definido no mapa",
                    "latInicial":       lat1,
                    "longInicial":      long1,
                    "textChegada":      "Definido no mapa",
                    "latFinal":         lat2,
                    "longFinal":        long2,
                    "calculoPartida":   0,
                    "dataRota":         datarota,
                    "horaRota":         horarota,
                    "meiosTransporte":  "true,true,true,true",
                    "tipoPercurso":     tipopercurso, 
                    }

    all_params={}; all_params.update(base_params); all_params.update(extra_params)
    request_params= urllib.urlencode(all_params)
    html = urllib.urlopen(method_url + "?" + request_params).read()
    return journey.parse(html)
