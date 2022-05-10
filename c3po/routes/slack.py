#!/usr/bin/env python3

import json

import flask
from flask import current_app as app, request, Response

from c3po.modules.slack import SlackApi, SlackEventHandler
from c3po.modules.helpers import verify_slack_signature


v1_slack = flask.Blueprint('v1_slack', __name__, url_prefix='/v1/slack')

@v1_slack.route('/events', methods=['POST'])
def event_api_handler():
    data = request.json
    slack_api = SlackApi(app.config['SLACK_TOKEN'])
    app.logger.info("Request payload: " + json.dumps(data))

    slack_signature = request.headers['X-Slack-Signature']
    slack_request_timestamp = request.headers['X-Slack-Request-Timestamp']

    slack_event = SlackEventHandler()

    if not verify_slack_signature(slack_signature=slack_signature, slack_request_timestamp=slack_request_timestamp):
        app.logger.info("Bad request")
        return Response(status=400)

    if data['type'] == 'url_verification':
        return Response(data['challenge'], mimetype='text/html')

    elif data['event']['type'] == 'app_mention':
        message = slack_event.mention_parser(request=data)
        status = slack_api.sendMessage(message)

        return Response(status, mimetype='application/json')
