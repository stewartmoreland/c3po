import json

from flask import current_app as app
from flask import Blueprint, request, make_response, Response

from slack_sdk.errors import SlackApiError

from c3po.modules.slack import SlackApi

v1_slack_messenger = Blueprint('v1_slack_messager', __name__, url_prefix='/v1/slack/messenger')

@v1_slack_messenger.route('/send', methods=['POST'])
def send_message_api():
    from c3po.database import installation_store

    data = request.json
    app.logger.debug("Request payload: " + json.dumps(data))

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
    message = slack_api.send_message(data['event']['text'])

    return Response(message, mimetype='application/json'), 200
