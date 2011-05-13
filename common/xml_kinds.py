import sqlalchemy
import xml_types

class xml_kind(object): pass

K= xml_kind
SB= sqlalchemy.types.Boolean
SD= sqlalchemy.types.Date
SS= sqlalchemy.types.String


#PES
class birthdate (SD, K):   type = xml_types.DATETIME_TYPE
class name      (SS, K): type = xml_types.STRING_TYPE
class office    (SS, K): type = xml_types.STRING_TYPE
class contact   (SS, K): type = xml_types.STRING_TYPE
class email     (SS, K): type = xml_types.EMAIL_TYPE
class phone     (SS, K): type = xml_types.STRING_TYPE
class fax       (SS, K): type = xml_types.STRING_TYPE

#CONCIERGE - SERVICES
class service_name  (SS, K): type = xml_types.STRING_TYPE
class service_url   (SS, K): type = xml_types.URL_TYPE
class service_active(SB, K): type = xml_types.BOOLEAN_TYPE
