from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy
import xml_types

app = Flask(__name__)
db = SQLAlchemy(app)

class birthdate (db.Date):   type = xml_types.DATETIME_TYPE
class name      (db.String): type = xml_types.STRING_TYPE
class office    (db.String): type = xml_types.STRING_TYPE
class contact   (db.String): type = xml_types.STRING_TYPE
class email     (db.String): type = xml_types.EMAIL_TYPE
class phone     (db.String): type = xml_types.STRING_TYPE
class fax       (db.String): type = xml_types.STRING_TYPE
