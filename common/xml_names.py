NAME_PROP_NAME= 'name'

pes_person=                     staticmethod(lambda obj: obj.name)

departamentos_department=       staticmethod(lambda obj: obj.name)
departamentos_course=           staticmethod(lambda obj: obj.name)
departamentos_subject=          staticmethod(lambda obj: obj.name)

geo_placemark=      staticmethod(lambda obj: "%s (%s)" % (obj.name, obj.folder))
geo_placemarktype=  staticmethod(lambda obj: obj.type_name)
