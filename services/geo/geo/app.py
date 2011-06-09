from flask import Flask, Response, request, url_for
from flaskext.sqlalchemy import SQLAlchemy
from common import search

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///geo.db'
db = SQLAlchemy(app)

class PlacemarkType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_name= db.Column(db.String(64))

    keywords= ['edificios', 'salas']
    search_atributes= ["type_name"]
    search_representative="placemark"

class Placemark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    folder= db.Column(db.String(128))
    name= db.Column(db.String(1024))
    abreviation= db.Column(db.String(32))
    type_id= db.Column( db.Integer, db.ForeignKey('placemark_type.id'))
    type= db.relationship('PlacemarkType', backref='placemark')
    geowkt= db.Column(db.String(8192))

    keywords= ['sitio','place', 'placemark', 'sala', 'edificio']
    search_joins= ["type"]
    search_atributes= ["name", "abreviation"]
    
    def permalink(self):
        return url_for('placemark', id = self.id)

    def to_xml_shallow(self):
        return '<entity type="string" service="Geo" url="%s">%s</entity>' %( self.permalink(), self.name )

    def to_xml(self):
        xml = '<entity type="map">'
        xml += '<entity type="string">%s</entity>' %self.name
        xml += '<entity type="string">%s</entity>' %self.folder
        xml += '<entity type="geowkt">%s</entity>' %self.geowkt
        if self.type:
            xml += '<entity type="string">%s</entity>' %self.type.type_name
        if self.abreviation:
            xml += '<entity type="string">%s</entity>' %self.abreviation
        xml += '</entity>'
        return xml


@app.route("/")
def search_method():
    q = request.args.get('query', '')   #quoted query
    model_list= [Placemark, PlacemarkType]
    xml= search.service_search_xmlresponse(model_list, q)
    return Response(response=xml, mimetype="application/xml")


@app.route("/placemarks", methods=['GET',])
def placemarks():
    #start = request.args.get('start', 0)
    #end = request.args.get('end', 10)
    placemarks = Placemark.query.all()
    xml = '<entity type="list">'
    for p in placemarks:
        xml += p.to_xml_shallow()
    xml += '</entity>'
    return Response(response=xml, mimetype="application/xml")

@app.route("/placemarks/<id>")
def placemark(id):
    placemark = Placemark.query.get_or_404(id)
    return Response(response=placemark.to_xml(), mimetype='application/xml')

    
