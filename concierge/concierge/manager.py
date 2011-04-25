from flaskext.script import Manager

from concierge import create_app, db


manager = Manager(create_app)
manager.add_option("-c", "--config", dest="cfg", required=False)


@manager.shell
def make_shell_context():
    from flask import current_app
    from concierge.auth import User
    from concierge.services import Service
    return dict(app=current_app, db=db, User=User, Service=Service)


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
    from concierge.auth import User
    from concierge.services import Service
    user = User('username', 'password')
    service = Service(name='pessoas', user=user, active=True,
                      url='http://127.0.0.1:5001/static/metadata.xml')
    db.session.add(user)
    db.session.add(service)
    db.session.commit()


if __name__ == "__main__":
    manager.run()
