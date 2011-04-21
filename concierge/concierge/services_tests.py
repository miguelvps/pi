import unittest

from flask import session
from flaskext.testing import TestCase

from concierge import create_app, db
from concierge.auth import User
from concierge.services import Service


class AuthTest(TestCase):

    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def create_app(self):
        return create_app(self)

    def setUp(self):
        db.create_all()
        user = User('username', 'password')
        service= Service('service1', 'http://service.com', user)
        db.session.add(user)
        db.session.add(service)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
   
    def test_showservice(self):
        with self.client as c:
            rv = c.get('/services/')
            print rv.data

if __name__ == '__main__':
    unittest.main()
