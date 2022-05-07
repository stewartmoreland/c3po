#!/usr/bin/env python3
""" Application configuration

This module is used to provide environment-based configuration objects
for the flask application context on start up.
"""
import os, json, secrets
from random import random

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    """
    Base Flask configuration class.
    Note: Base should always assume to be Production.
    """
    SESSION_COOKIE_SECURE = True
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or secrets.token_urlsafe(16)

    SLACK_CLIENT_ID = os.environ.get('SLACK_CLIENT_ID')
    SLACK_CLIENT_SECRET = os.environ.get('SLACK_CLIENT_SECRET')


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
    """
    Local configuration object for local development.
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
