#!/usr/bin/env python3

import json

from flask import Blueprint, make_response
from flask import current_app as app, request, Response

from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.errors import SlackApiError

from c3po.modules.slack import SlackApi, SlackEventHandler
from c3po.modules.helpers import verify_slack_signature


v1_slack = Blueprint('v1_slack', __name__, url_prefix='/v1/slack')

@v1_slack.route('/events', methods=['POST'])
def event_api_handler():
    data = request.json
    app.logger.debug("Request payload: " + json.dumps(data))

    slack_signature = request.headers['X-Slack-Signature']
    slack_request_timestamp = request.headers['X-Slack-Request-Timestamp']

    slack_event = SlackEventHandler()

    if not verify_slack_signature(slack_signature=slack_signature, slack_request_timestamp=slack_request_timestamp):
        app.logger.info("Bad request")
        return Response(status=400)

    if data['type'] == 'url_verification':
        return Response(data['challenge'], mimetype='text/html')

    elif data['event']['type'] == 'app_mention':
        installation_store = FileInstallationStore(base_dir="./data")
        try:
            # in the case where this app gets a request from an Enterprise Grid workspace
            enterprise_id = request.form.get("enterprise_id")
            # The workspace's ID
            team_id = request.form["team_id"]
            # Lookup the stored bot token for this workspace
            bot = installation_store.find_bot(
                enterprise_id=enterprise_id,
                team_id=team_id,
            )
            bot_token = bot.bot_token if bot else None
            if not bot_token:
                # The app may be uninstalled or be used in a shared channel
                return make_response("Please install this app first!", 200)
        except SlackApiError as e:
            app.logger.error(f"Error getting bot token: {e}")
            return make_response(f"Error getting bot token: {e}", 200)

        slack_api = SlackApi(token=bot_token)
        message = slack_event.mention_parser(request=data)
        status = slack_api.sendMessage(message)

        return Response(status, mimetype='application/json'), 200
