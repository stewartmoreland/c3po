#!/usr/bin/env python3
""" Flask app setup

This module is used to initialize the Flask app with the given
configuration and register handlers.
"""

from flask import Flask
from flask.json import JSONEncoder

from c3po.routes.root import v1_root


def create_app(config_object):
    """ Basic application factory for setting up the Flask app

    Args:
        config_object (object): The config object to load into the
            Flask app
        config_object (string): The string path to the config object
            to load into the flask app
    
    Returns:
        app (object): The Flask app post-setup
    """
    app = Flask(__name__)

    app.config.from_object(config_object)

    # Configuration to minify JSON output
    app.json_encoder = MinifyJSONEncoder
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

    # Init database
    with app.app_context():
        from c3po.database import db_session, init_db
        init_db()

    # Register api blueprints
    app.register_blueprint(v1_root)

    # Register global exception handler
    # AppExceptionHandler(app=app)

    @app.route('/health', methods=['GET'])
    def health_check():
        """ Root health check endpoint

        Returns:
            Response: Empty string and status code of 200
        """
        return 'up', 200

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app

class MinifyJSONEncoder(JSONEncoder):
    """Used to minify JSON output"""
    item_separator = ','
    key_separator = ':'
