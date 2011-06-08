from flaskext.script import Manager, Server

from geo.app import app, db, Placemark, PlacemarkType


manager = Manager(app)
manager.add_command("runserver", Server(port = 5004))

@manager.command
def syncdb():
    """Creates missing database tables."""
    db.create_all()


@manager.command
def resetdb():
    """Drops and creates the database."""
    db.drop_all()
    db.create_all()


@manager.command
def fixtures():
    """Loads sample data in the database."""
    from xml.etree import ElementTree
    
    db.drop_all()
    db.create_all()

    filename="geral-wkt-pi.xml"
    f= open(filename)
    xml=  ElementTree.fromstring(f.read())
    attrs_dicitionary= {"ID":"id", "KML_FOLDER": "folder", "Nome": "name", "Abreviatura": "abreviation", "Tipo": "type"}

    def add_to_db(attrs, geowkt):
        assert len(geowkt)<8192
        db_atrs= dict(zip([attrs_dicitionary[k] for k in attrs.keys()], attrs.values()))
        t= db_atrs.get('type')
        if t:
            type= PlacemarkType.query.filter_by(type_name=t).first()
            if not type:
                type= PlacemarkType(type_name=t)
                db.session.add(type)
                db.session.commit()
            db_atrs['type']=type
            
        db_atrs['geowkt']= geowkt
        print db_atrs
        p = Placemark(**db_atrs)
        db.session.add(p)

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
            add_to_db(attrs, geowkt)
    db.session.commit()


if __name__ == "__main__":
    manager.run()
