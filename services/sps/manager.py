from flaskext.script import Manager, Server

from sps.app import app, db

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

if __name__ == "__main__":
    manager.run()
