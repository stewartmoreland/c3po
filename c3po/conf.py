#!/usr/bin/env python3
""" Application configuration

This module is used to provide environment-based configuration objects
for the flask application context on start up.
"""
import os
import json

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    """ 
    Base Flask configuration object. 
    Note: Base should always assume to be Production.
    """
    SESSION_COOKIE_SECURE = True
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SLACK_CLIENT_ID = os.environ.get('SLACK_CLIENT_ID')
    SLACK_CLIENT_SECRET = os.environ.get('SLACK_CLIENT_SECRET')
    SLACK_SIGNING_SECRET = os.environ.get('SLACK_SIGNING_SECRET')


class ProductionConfig(Config):
    """ 
    Production configuration object.
    """
    PORT = os.environ.get('PORT') or '5000'


class DevelopmentConfig(Config):
    """
    Development configuration object.
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
