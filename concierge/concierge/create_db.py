from concierge import create_app, db
from concierge.auth import User
from concierge.services import Service



def reset(fill_fixtures=False):
    app = create_app()
    ctx = app.test_request_context()
    ctx.push()

    db.drop_all()
    db.create_all()
    if fill_fixtures:
        user = User('username', 'password')
        service = Service(name='service1', url='http://service.com',
                          user=user, active=True)
        db.session.add(service)
        db.session.add(user)
        db.session.commit()
        db.session.remove()

    ctx.pop()

if __name__=="__main__":
    reset(fill_fixtures=True)
