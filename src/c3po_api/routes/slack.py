#!/usr/bin/env python3

import json

import flask
from flask import current_app as app, request, Response

from c3po_api.modules.slack import SlackApi, SlackEventHandler
from c3po_api.modules.helpers import verify_slack_signature


v1_slack = flask.Blueprint('v1_slack', __name__, url_prefix='/api/v1')

@v1_slack.route('/slack/events', methods=['POST'])
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
    
    elif data['event']['type'] == 'message':
        response = slack_event.message_parser(request=data)

        return Response(response=response, mimetype='application/json')

@v1_slack.route('/user/import', methods=['POST'])
def slack_user_import():
    from c3po_api.database import db_session
    from c3po_api.database.model import User
    client = SlackApi(app.config['SLACK_TOKEN'])
    user_count = int(0)

    all_users = client.getAllUsers()

    for user in all_users:
        if user['is_bot'] is True:
            app.logger.debug("Skipping bot user")
        elif User.query.filter(User.slack_id == user['id']).first() is None:
            item = User(slack_id=user['id'],
                        user_name=user['name'],
                        slack_subscription=user['team_id'],
                        full_name=user['profile']['real_name_normalized'])
            db_session.add(item)
            db_session.commit()

            user_count += 1
    
    response = {
        "status": "200",
        "body": "Total users imported: " + str(user_count)
    }
    return Response(response=json.dumps(response), mimetype='application/json')
