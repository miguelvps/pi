import sqlalchemy
import xml_types

class xml_kind(object): pass

def set_model_kind(model_class, kind):
    model_class.kind= kind

def get_model_kind(model_class):
    return getattr(model_class,'kind',None)



K= xml_kind
SB= sqlalchemy.types.Boolean
SD= sqlalchemy.types.Date
SS= sqlalchemy.types.String


#PES
class birthdate (SD, K): type = xml_types.DATETIME_TYPE
class name      (SS, K): type = xml_types.STRING_TYPE
class office    (SS, K): type = xml_types.STRING_TYPE
class contact   (SS, K): type = xml_types.STRING_TYPE
class email     (SS, K): type = xml_types.EMAIL_TYPE
class phone     (SS, K): type = xml_types.STRING_TYPE
class fax       (SS, K): type = xml_types.STRING_TYPE
class person    (K):     type = xml_types.LIST_TYPE ; representative = staticmethod(lambda obj: obj.name)

#ORG

##DEPARTMENT
class dep_name          (SS, K): type = xml_types.STRING_TYPE
class dep_acronym       (SS, K): type = xml_types.STRING_TYPE 
class department        (K):     type = xml_types.LIST_TYPE ; representative = staticmethod(lambda obj: obj.name)

##COURSE
class course_name       (SS, K): type = xml_types.STRING_TYPE
class course_acronym    (SS, K): type = xml_types.STRING_TYPE 
class course_type       (SS, K): type = xml_types.STRING_TYPE
class course            (K):     type = xml_types.LIST_TYPE ; representative = staticmethod(lambda obj: obj.name)

##SUBJECT
class subject_name        (SS, K): type = xml_types.STRING_TYPE
class subject_acronym     (SS, K): type = xml_types.STRING_TYPE
class subject_period      (SS, K): type = xml_types.STRING_TYPE
class subject_regent      (SS, K): type = xml_types.STRING_TYPE  
class subject_coordinator (SS, K): type = xml_types.STRING_TYPE  
class subject             (K):     type = xml_types.LIST_TYPE ; representative = staticmethod(lambda obj: obj.name)

#CONCIERGE - SERVICES
class service_name  (SS, K): type = xml_types.STRING_TYPE
class service_url   (SS, K): type = xml_types.URL_TYPE
class service_active(SB, K): type = xml_types.BOOLEAN_TYPE

#GEO
class geo_name(SS, K): type = xml_types.STRING_TYPE
class geo_folder(SS, K): type = xml_types.STRING_TYPE
class geo_abreviation(SS, K): type = xml_types.STRING_TYPE
class geo_wkt(SS, K): type = xml_types.STRING_TYPE


class geo_placemark(K): type = xml_types.LIST_TYPE ; representative = staticmethod(lambda obj: "%s (%s)" % (obj.name, obj.folder))
