from flaskext.script import Manager

from org.app import app, db


manager = Manager(app)

'''
@manager.shell
def make_shell_context():
    from flask import current_app
    from org.app import Department, Course, Subject
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
    from org.app import Department, Course, Subject
    
    reader = csv.reader(open('cursos.csv', 'r'), delimiter=',')
    for row in reader:
        department_name = row[4].decode('utf-8')
        
        departament = Department.query.filter_by(name=department_name).first()
        if not department:
            department = Department(name=departmen_name)
            db.session.add(department)
            db.session.commit()

        type = row[2].decode('utf-8')    
        course_type = CourseType.query.filter_by(name=type).first() 

        if not course_type:
            course_type = CourseType(name=type)
            db.session.add(course_type)
            db.session.commit()

        course = Course(id=row[0].decode('utf-8'), acronym=row[1].decode('utf-8'),
                        type=course_type, name=row[3].decode('utf-8'),
                        department=department)

        db.session.add(course)
    db.session.commit()
        
        
'''
if __name__ == "__main__":
    manager.run()

