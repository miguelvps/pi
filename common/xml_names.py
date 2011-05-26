NAME_PROP_NAME= 'xml_name'

pes_person=                     lambda obj: obj.name

departamentos_department=       lambda obj: obj.name
departamentos_course=           lambda obj: obj.name
departamentos_subject=          lambda obj: obj.name

geo_placemark=      lambda obj: "%s (%s)" % (obj.name, obj.folder)
geo_placemarktype=  lambda obj: obj.type_name
