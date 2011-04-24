import unittest
from datetime import datetime

from flask import session, url_for
from flaskext.testing import TestCase

from concierge import create_app, db
from concierge.auth import User, requires_auth


class AuthTest(TestCase):

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

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
        user = User('username', 'randompw')
        db.session.add(user)
        self.assertRaises(Exception, db.session.commit)
        db.session.rollback()

        utc = datetime.utcnow()
        user = User('newuser', 'randompw')
        assert datetime.utcnow() > user.created > utc
        assert user.username == 'newuser'
        assert user.check_password('randompw') == True
        assert user.check_password('wrongpw') == False
        db.session.add(user)
        db.session.commit()

        user = User.query.filter_by(username='newuser').first()
        assert user.username == 'newuser'
        assert datetime.utcnow() > user.created > utc
        assert user.check_password('randompw') == True
        assert user.check_password('wrongpw') == False

        user = User.query.filter_by(username='wronguser').first()
        assert user == None

    def test_requires_auth(self):
        @requires_auth
        def require_auth():
            return ""
        with self.client:
            rv = require_auth()
            assert rv.status_code == 302
            assert ('Location', url_for('auth.login')) in rv.header_list

            session['auth'] = True
            rv = require_auth()
            assert rv == ""

    def test_login_logout(self):
        with self.client as c:
            c.post(url_for('auth.login'), data=dict(
                username='username',
                password='password'))
            assert session.get('auth') == True
            assert session.get('username') == 'username'
            assert session.permanent == False

            c.post(url_for('auth.login'), data=dict(
                username='username',
                password='password',
                remember=True))
            assert session.permanent == True

            c.get(url_for('auth.logout'))
            assert session.get('auth') == None

            c.get(url_for('auth.logout'))
            assert session.get('auth') == None

            c.post(url_for('auth.login'), data=dict(
                username='username',
                password='wrongpw',
                remember=True))
            assert session.get('auth') == None

            c.post(url_for('auth.login'), data=dict(
                username='wronguser',
                password='password'))
            assert session.get('auth') == None

    def test_register(self):
        with self.client as c:
            c.post(url_for('auth.register'), data=dict(
                username='username',
                password='randompw',
                confirm='randompw'))
            assert session.get('auth') == None
            user = User.query.filter_by(username='username').first()
            assert user.check_password('password') == True

            c.post(url_for('auth.register'), data=dict(
                username='newuser',
                password='newpass',
                confirm='badconfirm'))
            assert session.get('auth') == None
            user = User.query.filter_by(username='newuser').first()
            assert user == None

            c.post(url_for('auth.register'), data=dict(
                username='newuser',
                password='newpass',
                confirm='newpass',
                remember=None))
            assert session.get('auth') == True
            assert session.get('username') == 'newuser'
            user = User.query.filter_by(username='newuser').first()
            assert user.username == 'newuser'
            assert session.permanent == False

            c.post(url_for('auth.register'), data=dict(
                username='remember',
                password='remember',
                confirm='remember',
                remember=True))
            assert session.permanent == True

    def test_last_seen(self):
        with self.client as c:
            utc = datetime.utcnow()
            c.post(url_for('auth.login'), data=dict(
                username='username',
                password='password',
                remember=True))
            user = User.query.filter_by(username='username').first()
            assert datetime.utcnow() > user.last_seen > utc

            utc = datetime.utcnow()
            c.get('/')
            user = User.query.filter_by(username='username').first()
            assert datetime.utcnow() > user.last_seen > utc



if __name__ == '__main__':
    unittest.main()
