import sqlalchemy
import xml_types

class birthdate (sqlalchemy.types.Date):   type = xml_types.DATETIME_TYPE
class name      (sqlalchemy.types.String): type = xml_types.STRING_TYPE
class office    (sqlalchemy.types.String): type = xml_types.STRING_TYPE
class contact   (sqlalchemy.types.String): type = xml_types.STRING_TYPE
class email     (sqlalchemy.types.String): type = xml_types.EMAIL_TYPE
class phone     (sqlalchemy.types.String): type = xml_types.STRING_TYPE
class fax       (sqlalchemy.types.String): type = xml_types.STRING_TYPE
