import unittest

from flask import session
from flaskext.testing import TestCase

from concierge import create_app, db
from concierge.auth import User
from concierge.services import Service


class AuthTest(TestCase):

    TESTING = True

    def create_app(self):
        return create_app(self)

    def setUp(self):
        create_db.reset(fill_fixtures=True)

    def tearDown(self):
        db.drop_all()
   
    def test_listservices(self):
        with self.client as c:
            rv = c.get('/services/')

    def test_showservice(self):
        with self.client as c:
            rv = c.get('/services/1/')

if __name__ == '__main__':
    unittest.main()
