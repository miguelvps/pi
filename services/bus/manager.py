from flaskext.script import Manager, Server

from bus.app import app


manager = Manager(app)
manager.add_command("runserver", Server(port = 3006))

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
    


if __name__ == "__main__":
    manager.run()
