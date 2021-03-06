from flaskext.script import Manager, Server

from departamentos.app import app, db

manager = Manager(app)
manager.add_command("runserver", Server(port = 3005))

@manager.shell
def make_shell_context():
    from flask import current_app
    from departamentos.app import Department, Course, Subject
    return dict(app=current_app, db=db, Department=Department,
                Course=Course, Subject=Subject)

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
    from departamentos.app import Department, Course, CourseType, Subject

    reader = csv.reader(open('cursos.csv', 'r'), delimiter=',')
    for row in reader:
        department_name = row[4].decode('utf-8')
        department = Department.query.filter_by(name=department_name).first()
        if not department:
            department = Department(name=department_name)
            db.session.add(department)
            db.session.commit()

        type = row[3].decode('utf-8')
        course_type = CourseType.query.filter_by(name=type).first()
        if not course_type:
            course_type = CourseType(name=type)
            db.session.add(course_type)
            db.session.commit()

        course = Course(id=row[0].decode('utf-8'), acronym=row[1].decode('utf-8'),
                        type=course_type, name=row[2].decode('utf-8'),
                        department=department)
        db.session.add(course)
    db.session.commit()

    reader = csv.reader(open('cadeiras.csv', 'r'), delimiter=',')
    for row in reader:
        course = Course.query.filter_by(name=row[4].decode('utf-8')).first()
        if not course:
            print "Invalid course:", row[4].decode('utf-8')
            continue

        subject_id = row[1].decode('utf-8')
        subject = Subject.query.filter_by(id=subject_id).first()
        if not subject:
            subject = Subject(id=subject_id, name=row[3].decode('utf-8'), acronym=row[2].decode('utf-8'),
                              regent=row[5].decode('utf-8'), coordinator=row[6].decode('utf-8'),
                              period=row[0].decode('utf-8'))
        subject.courses.append(course)
        db.session.add(subject)
        db.session.commit()


if __name__ == "__main__":
    manager.run()
