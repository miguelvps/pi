import csv

from pes.app import db, Teacher, Email


db.drop_all()
db.create_all()

reader = csv.reader(open('docentes.csv', 'r'), delimiter=',')
for row in reader:
    id = row[0]
    name = row[1].decode('utf-8')
    print name.encode('utf-8')
    email = row[2].decode('utf-8')

    teacher = Teacher.query.get(id)
    if not teacher:
        e = Email(email=email)
        teacher = Teacher(id=id, name=name, emails=[Email(email=email)])
    else:
        e = Email.query.filter_by(email=email).first()
        if not e:
            teacher.emails.append(Email(email=email))

    db.session.add(teacher)
    db.session.commit()
