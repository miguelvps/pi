import csv

from pes.app import db, Teacher, Email


db.drop_all()
db.create_all()

reader = csv.reader(open('docentes.csv', 'r'), delimiter=',')
for row in reader:
    e = Email(email=row[2].decode('utf-8'))
    t = Teacher(name=row[1].decode('utf-8'), emails=[e])
    db.session.add(t)
    db.session.add(e)
db.session.commit()
