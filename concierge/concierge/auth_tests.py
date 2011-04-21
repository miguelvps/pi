import unittest

from flask import session
from flaskext.testing import TestCase

from concierge import create_app, db
from concierge.auth import User


class AuthTest(TestCase):

    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def create_app(self):
        return create_app(self)

    def setUp(self):
        db.create_all()
        user = User('username', 'password')
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_user(self):
        user = User.query.filter_by(username='username').first()
        assert user.username == 'username'
        assert user.check_password('password') == True
        assert user.check_password('wrongpw') == False

    def test_login_logout(self):
        with self.client as c:
            c.post('/auth/login', data=dict(
                username='username',
                password='password'))
            assert session.get('auth') == True
            assert session.get('username') == 'username'

            c.get('/auth/logout', follow_redirects=True)
            assert session.get('auth') == None

            c.post('/auth/login', data=dict(
                username='username',
                password='wrongpw'))
            assert session.get('auth') == None

            c.post('/auth/login', data=dict(
                username='wronguser',
                password='password'))
            assert session.get('auth') == None

    def test_register(self):
        with self.client as c:
            rv = c.get('/auth/register')
            assert "register" in rv.data

            c.post('/auth/register', data=dict(
                username='newuser',
                password='password',
                confirm='password'))
            assert session.get('auth') == True
            assert session.get('username') == 'newuser'


if __name__ == '__main__':
    unittest.main()
