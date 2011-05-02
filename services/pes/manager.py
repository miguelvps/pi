from flaskext.script import Manager

from pes.app import app, db


manager = Manager(app)


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
    import csv
    from pes.app import Teacher, Email
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


if __name__ == "__main__":
    manager.run()
