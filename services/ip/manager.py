
from flaskext.script import Manager, Server

from ip.app import app, db, Deadline, Requisite, Document, Process, RequisiteDocument
import datetime

manager = Manager(app)

manager.add_command("runserver", Server(port = 5003))

@manager.shell
def make_shell_context():
    from flask import current_app
    from sps.app import Process, Document, Requisite, Deadline
    return dict(app=current_app, db=db, Process=Process,
                Document=Document, Requisite=Requisite, Deadline=Deadline)

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
    """Drops and creates the database."""
    db.drop_all()
    db.create_all()
    
    doc1= Document(name='Notas de acesso', url='http://www.fct.unl.pt/sites/default/files/Crit%C3%A9rios%20m%C3%ADnimos%20e%20F%C3%B3rmulas%20nota_%20candidatura_2011_12.pdf')
    doc2= Document(name= 'Provas de ingresso', url='http://www.fct.unl.pt/sites/default/files/prov_%20ingr_%202011_12_oficial.pdf')
    rd1= RequisiteDocument(description=u'Documento de identificação + 2 fotocópias (B.I., Cartão de Cidadão ou Passaporte)')
    rd2= RequisiteDocument(description=u'Documento de identificação + 2 fotocópias (B.I., Cartão de Cidadão ou Passaporte)')
    rd3= RequisiteDocument(description=u'2 (duas) fotografias actualizadas, tipo passe')
    rd4= RequisiteDocument(description=u'Boletim individual de saúde c/ a vacina do tétano em dia (original + 1 fotocópia)')
    d1= Deadline(name=u"Propina - 1.ª Prestação: 333,24€", date=datetime.date(2011, 10, 5))
    d2= Deadline(name=u"Propina - 2.ª Prestação: 333,24€", date=datetime.date(2011, 12, 5))
    d3= Deadline(name=u"Propina - 3.ª Prestação: 333,24€", date=datetime.date(2012, 03, 6))
    p= Process(name='Matricula Licenciatura', deadlines=[d1,d2,d3], documents=[doc1,doc2],  requisite_documents=[rd1,rd2,rd3,rd4],  url='http://www.fct.unl.pt/candidato/1o-ciclo-licenciaturas')
    db.session.add(p)
    db.session.commit()

if __name__=='__main__':
    manager.run()
