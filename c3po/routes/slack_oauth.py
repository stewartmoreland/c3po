from cmath import log
import os

from flask import current_app as app
from flask import Blueprint, make_response, request, redirect, render_template

from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.oauth.installation_store import Installation

from slack_sdk.web import WebClient


# Build https://slack.com/oauth/v2/authorize with sufficient query parameters
authorize_url_generator = AuthorizeUrlGenerator(
    client_id=os.environ["SLACK_CLIENT_ID"],
    scopes=["app_mentions:read", "chat:write"],
    user_scopes=["search:read"],
)

v1_slack_oauth = Blueprint("v1_slack_oauth", __name__,
                           url_prefix="/v1/slack/oauth")


@v1_slack_oauth.route("/authorize", methods=["GET"])
def authorize():
    """
    Redirect the user to the Slack OAuth flow.
    """
    from c3po.database import state_store
    state = state_store.issue()
    return redirect(authorize_url_generator.generate(state))


@v1_slack_oauth.route("/callback", methods=["GET"])
def oauth_callback():
    """
    Exchange the OAuth code for an OAuth token.
    """
    from c3po.database import state_store, installation_store

    client_secret = app.config["SLACK_CLIENT_SECRET"]
    if "code" in request.args:
        if state_store.consume(request.args["state"]):
            client = WebClient()

            # Complete the installation by calling oauth.v2.access API method
            oauth_response = client.oauth_v2_access(
                client_id=authorize_url_generator.client_id,
                client_secret=client_secret,
                redirect_uri=authorize_url_generator.redirect_uri,
                code=request.args["code"]
            )

            installed_enterprise = oauth_response.get("enterprise", {})
            is_enterprise_install = oauth_response.get("is_enterprise_install")
            installed_team = oauth_response.get("team", {})
            installer = oauth_response.get("authed_user", {})
            incoming_webhook = oauth_response.get("incoming_webhook", {})

            # NOTE: oauth.v2.access doesn't include bot_id in response
            bot_token = oauth_response.get("access_token")
            bot_id = None

            enterprise_id = None
            enterprise_name = None
            enterprise_url = None
            if bot_token is not None:
                auth_test = client.auth_test(token=bot_token)
                bot_id = auth_test["bot_id"]
                if is_enterprise_install is True:
                    enterprise_id = installed_enterprise.get("id")
                    enterprise_name = installed_enterprise.get("name")
                    enterprise_url = auth_test.get("url")


            installation = Installation(
                app_id=oauth_response.get("app_id"),
                enterprise_id=enterprise_id,
                enterprise_name=enterprise_name,
                enterprise_url=enterprise_url,
                team_id=installed_team.get("id"),
                team_name=installed_team.get("name"),
                bot_token=bot_token,
                bot_id=bot_id,
                bot_user_id=oauth_response.get("bot_user_id"),
                bot_scopes=oauth_response.get("scope"),
                user_id=installer.get("id"),
                user_token=installer.get("access_token"),
                user_scopes=installer.get("scope"),
                incoming_webhook_url=incoming_webhook.get("url"),
                incoming_webhook_channel=incoming_webhook.get("channel"),
                incoming_webhook_channel_id=incoming_webhook.get("channel_id"),
                incoming_webhook_configuration_url=incoming_webhook.get(
                    "configuration_url"),
                is_enterprise_install=is_enterprise_install,
                token_type=oauth_response.get("token_type"),
            )

            # Store the installation
            installation_store.save(installation)

            return render_template('install_result.html', template_header="SUCCESS!", template_body="Hello. I don’t believe we have been introduced. A pleasure to meet you. I am C-3PO, Human-Cyborg Relations."), 200
        else:
            return render_template('install_result.html', template_header="R2D2, you know better than to trust a strange computer!", template_body="Try the installation again (the state value is already expired)"), 400

    error = request.args["error"] if "error" in request.args else ""
    return render_template('install_result.html', template_header="Wait. Oh my! What have you done...I am backwards you filthy furball.", template_body=f"Something is wrong with the installation (error: {error})"), 400
