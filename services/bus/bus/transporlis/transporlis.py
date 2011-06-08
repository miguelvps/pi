import urllib
import journey

urlbase= "http://transporlis.sapo.pt:80/"
UrlBaseAjax= urlbase + "DesktopModules/trp_calculo_percurso/"
iskyosk= "false"

base_params=    {
                    "cmd": "recuperarRota",
                    'UrlBase': urlbase,
                    'isKyosk': iskyosk,
                }

method_url= UrlBaseAjax + 'Ajax/trp_calculo_percurso.ashx'

def transportation(lat1, long1, lat2, long2, journey_datetime):
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

