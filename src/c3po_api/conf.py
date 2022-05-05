#!/usr/bin/env python3
""" Application configuration

This module is used to provide environment-based configuration objects
for the flask application context on start up.
"""
import os
import json

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    """ Base Flask configuration object. Base should always
    assume to be Production.
    """
    SESSION_COOKIE_SECURE = True
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SLACK_TOKEN = os.environ.get('SLACK_TOKEN')
    SLACK_SIGNING_SECRET = os.environ.get('SLACK_SIGNING_SECRET')
    REWARD_EMOJI = os.environ.get('REWARD_EMOJI') or ":taco:"


class ProductionConfig(Config):
    """ Producation config object
    """
    PORT = os.environ.get('PORT') or '5000'


class DevelopmentConfig(Config):
    """ Development config object
    """
    DEBUG = True


class LocalConfig(Config):
    """ Local configuration object for local development.
    """
    DEBUG = True
    PORT = 5000
    URL_SCHEME = 'http'
    SESSION_COOKIE_SECURE = False


config = {
    'LOCAL': LocalConfig,
    'DEVELOPMENT': DevelopmentConfig,
    'PRODUCTION': ProductionConfig,
    'default': LocalConfig
}
""" dict: For string key to object config mapping
"""
