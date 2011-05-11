import unittest

from flaskext.testing import TestCase

from concierge import create_app, db
from concierge.auth import User
from concierge.services import Service
from concierge.service_metadata_parser import parse_metadata
from concierge.common import rest_methods, rest_return_formats, rest_method_parameters


metadata = """
<service name="name" url="http://127.0.0.1/">
    <description>description</description>
    <supported_formats>
        <format>xml</format>
        <format>json</format>
    </supported_formats>

    <resource url="">
        <keywords>
            <keyword>keyword1</keyword>
            <keyword>keyword2</keyword>
            <keyword>keyword3</keyword>
            <keyword>keyword4</keyword>
        </keywords>
        <method type="GET" >
            <parameter>query</parameter>
        </method>
        <resource url="resource">
            <method type="GET" >
                <parameter>start</parameter>
                <parameter>end</parameter>
            </method>
        </resource>
    </resource>
</service>
"""


class ServicesTest(TestCase):

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

    def create_app(self):
        return create_app(self)

    def setUp(self):
        db.create_all()
        service = parse_metadata(metadata)
        service.metadata_url = "http://127.0.0.1/"
        service.user = User('username', 'password')

        db.session.add(service)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_metadata_parser(self):
        service = Service.query.first()
        assert service.name == "name"
        assert service.url == "http://127.0.0.1/"
        assert len(service.formats) == 2
        assert getattr(rest_return_formats, "xml") in [format.format for format in service.formats]
        assert getattr(rest_return_formats, "json") in [format.format for format in service.formats]
        assert len(service.resources) == 1
        resource = service.resources[0]
        assert len(resource.keywords) == 4
        assert "keyword1" in [keyword.keyword for keyword in resource.keywords]
        assert "keyword3" in [keyword.keyword for keyword in resource.keywords]
        assert len(resource.methods) == 1
        method = resource.methods[0]
        assert method.type == getattr(rest_methods, "GET")
        assert len(method.parameters) == 1
        parameter = method.parameters[0]
        assert parameter.parameter == getattr(rest_method_parameters, "query")

    def test_favorites(self):
        service = Service.query.first()
        user = User.query.first()
        assert len(service.users_favorite) == 0
        assert len(user.favorite_services) == 0

        service.users_favorite.append(user)
        assert len(service.users_favorite) == 1
        assert len(user.favorite_services) == 1
        assert service.users_favorite == [user]
        assert user.favorite_services == [service]


if __name__ == '__main__':
    unittest.main()
