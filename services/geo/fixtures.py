from xml.etree import ElementTree
from geo.app import db, Placemark, PlacemarkType


db.drop_all()
db.create_all()

filename="geral-wkt-pi.xml"
f= open(filename)
xml=  ElementTree.fromstring(f.read())

attrs_dicitionary= {"ID":"id", "KML_FOLDER": "folder", "Nome": "name", "Abreviatura": "abreviation", "Tipo": "type"}

def add_to_db(attrs, geowkt):
    db_atrs= zip([attrs_dicitionary[k] for k in attrs.keys()], attrs.values())
    p = Placemark(*db_atrs)

for folder_xml in xml:
    assert folder_xml.tag=='Folder'
    for placemark_xml in folder_xml.findall('Placemark'):
        description_xml= placemark_xml.find("description")
        #import ipdb ; ipdb.set_trace()
        attrs= {}
        for description_piece_xml in description_xml:
            assert description_piece_xml.tag=="meta-information"
            attrs[description_piece_xml.get('attribute')]= description_piece_xml.get('value')
        geowkt= placemark_xml.find('geo-wkt').text
        print attrs, geowkt
        add_to_db(attrs, geowkt)

    '''
    teacher = Teacher.query.get(id)
    if not teacher:
        e = Email(email=email)
        teacher = Teacher(id=id, name=name, emails=[Email(email=email)])
    else:
        e = Email.query.filter_by(email=email).first()
        if not e:
            teacher.emails.append(Email(email=email))

    db.session.add(teacher)
    '''
db.session.commit()
