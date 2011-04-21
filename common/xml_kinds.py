import sqlalchemy
import xml_types

#PES
class birthdate (sqlalchemy.types.Date):   type = xml_types.DATETIME_TYPE
class name      (sqlalchemy.types.String): type = xml_types.STRING_TYPE
class office    (sqlalchemy.types.String): type = xml_types.STRING_TYPE
class contact   (sqlalchemy.types.String): type = xml_types.STRING_TYPE
class email     (sqlalchemy.types.String): type = xml_types.EMAIL_TYPE
class phone     (sqlalchemy.types.String): type = xml_types.STRING_TYPE
class fax       (sqlalchemy.types.String): type = xml_types.STRING_TYPE

#CONCIERGE - SERVICES
class service_name  (sqlalchemy.types.String): type = xml_types.STRING_TYPE
class service_url   (sqlalchemy.types.String): type = xml_types.URL_TYPE
class service_active(sqlalchemy.types.Boolean): type = xml_types.BOOLEAN_TYPE
