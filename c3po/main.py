#!/usr/bin/env python3
import os

from c3po.flaskr import create_app
from c3po.conf import config

def main():
    environment_name = os.environ.get('ENVIRONMENT', 'default')
    config_object = config[environment_name]
    app = create_app(config_object)

    return app


if __name__ == '__main__':
    app = main()
    app.run(host='0.0.0.0', port=app.config['PORT'])
