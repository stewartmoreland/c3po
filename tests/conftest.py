import os

from pytest import fixture
from unittest import mock

from c3po.flaskr import create_app
from c3po.conf import Config


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

    SLACK_CLIENT_ID = "x-slack-client-id"
    SLACK_CLIENT_SECRET = "x-slack-client-secret"
    SLACK_SIGNING_SECRET = "x-slack-signing-secret"


@fixture(scope='session')
def app(request):
    with mock.patch.dict(os.environ, {'SLACK_CLIENT_ID': "x-slack-client-id"}):
        app = create_app(TestingConfig)
        return app


@fixture(autouse=True)
def app_context(request, app):
    ctx = app.app_context()
    ctx.push()
    yield
    ctx.pop()
