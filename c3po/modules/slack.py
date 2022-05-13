#! python3
import json
import logging
import hashlib
import hmac
import re
from time import sleep
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError

from flask import current_app as app

from c3po.modules.quotes import get_star_wars_quote


logger = logging.getLogger()
logger.setLevel(logging.INFO)

class SlackApi(object):
    def __init__(self, token):
        """
        Initializes the SlackApi object.
        """
        if not token:
            raise EnvironmentError()
        self._headers = {}
        self._headers["Authorization"] = "Bearer {}".format(token)

    def get_all_users(self):
        """
        Returns a list of all users.
        """
        members = list()
        endpoint = 'https://slack.com/api/users.list'
        variables = urlencode({'limit':'1000'})
        variables = variables.encode('ascii')
        page_count = 1
        
        while True:
            request = Request(endpoint, headers=self._headers, data=variables)
            with urlopen(request) as response:
                data = json.loads(response.read().decode('utf8'))
            nodes = data['members']
            for node in nodes:
                if node['deleted'] != True and node['is_bot'] != True:
                    members.append(node)
            app.logger.info(f"[SlackApi] [users.list] Processed page {page_count} with {len(nodes)} user records.")
            if data['response_metadata']['next_cursor']:
                variables = urlencode({'cursor':data['response_metadata']['next_cursor'],'limit':'1000'})
                variables = variables.encode('ascii')
                page_count = page_count + 1
                sleep(3)
            else:
                break

        return members

    def get_current_bot_info(self):
        """
        Returns the bot's information.
        """
        endpoint = 'https://slack.com/api/auth.test'
        self._headers["Content-Type"] = "application/x-www-form-urlencoded"
        request = Request(endpoint, headers=self._headers)
        with urlopen(request) as response:
            data = json.loads(response.read().decode('utf8'))
        return data

    def get_bot_info(self, bot_id):
        """
        Returns information about a bot.
        
        Args:
            bot_id (str): The bot ID to get information about.
            
        Returns:
            dict: A dictionary containing the bot's information.
        """
        endpoint = 'https://slack.com/api/bots.info'
        endpoint = endpoint + '?bot={}'.format(bot_id)
        self._headers["Content-Type"] = "application/x-www-form-urlencoded"
        request = Request(endpoint, headers=self._headers)
        with urlopen(request) as response:
            data = json.loads(response.read().decode('utf8'))
        return data

    def get_user_info(self, user_id):
        """
        Returns information about a user.

        Args:
            user_id (str): The user ID to get information about.

        Returns:
            dict: A dictionary containing the user's information.
        """
        endpoint = 'https://slack.com/api/users.info'
        variables = urlencode({'user':user_id})
        variables = variables.encode('ascii')
        user_data = {}

        request = Request(endpoint, headers=self._headers, data=variables)
        with urlopen(request) as response:
            user_data = json.loads(response.read().decode('utf8'))
        
        return user_data

    def get_conversation_info(self, user_id):
        """
        Returns the channel ID for a given user ID.
        
        Args:
            user_id (str): The user ID.
            
        Returns:
            str: The channel ID.
        """
        endpoint = 'https://slack.com/api/users.conversations'
        variables = urlencode({'user':user_id,'types':'im,mpim'})
        variables = variables.encode('ascii')
        convo_data = []

        while True:
            request = Request(endpoint, headers=self._headers, data=variables)
            with urlopen(request) as response:
                data = json.loads(response.read().decode('utf8'))
            nodes = data['channels']
            convo_data += nodes
            if data['response_metadata']['next_cursor']:
                variables = urlencode({'user':user_id,'types':'im,mpim','cursor':data['response_metadata']['next_cursor']})
                variables = variables.encode('ascii')
            else:
                break

        return convo_data

    def get_channel_id_by_name(self, channel_name):
        """
        Returns the channel ID for a given channel name.
        
        Args:
            channel_name (str): The name of the channel.
            
        Returns:
            str: The channel ID.
        """
        endpoint = 'https://slack.com/api/conversations.list'
        variables = urlencode({'types':'public_channel,private_channel'})
        variables = variables.encode('ascii')
        channel_list = list()

        while True:
            request = Request(endpoint, headers=self._headers, data=variables)
            with urlopen(request) as response:
                data = json.loads(response.read().decode('utf8'))
            nodes = data['channels']
            channel_list += nodes
            if data['response_metadata']['next_cursor']:
                variables = urlencode({'types':'public_channel,private_channel','cursor':data['response_metadata']['next_cursor']})
                variables = variables.encode('ascii')
            else:
                break

        try:
            for channel in channel_list:
                if channel['name'] == channel_name:
                    channel_id = channel['id']
            
            return channel_id
        except KeyError as e:
            app.logger.error(f'ERROR: {e} - Unable to find channel {channel_name}. If this is a private channel, try adding the bot user to the channel to make it visible.')

    def get_channel_list(self):
        """
        Returns a list of all channels the bot is in.
        
        Returns:
            list: A list of channel names.
        """
        endpoint = 'https://slack.com/api/conversations.list'
        variables = urlencode({'types':'public_channel,private_channel'})
        variables = variables.encode('ascii')
        channel_list = list()

        while True:
            request = Request(endpoint, headers=self._headers, data=variables)
            with urlopen(request) as response:
                data = json.loads(response.read().decode('utf8'))
            nodes = data['channels']
            channel_list += nodes
            if data['response_metadata']['next_cursor']:
                variables = urlencode({'types':'public_channel,private_channel','cursor':data['response_metadata']['next_cursor']})
                variables = variables.encode('ascii')
            else:
                break

        return channel_list

    def open_direct_message(self, user_ids):
        """
        Opens a direct message channel with the specified user(s).
        
        Args:
            user_ids (list): A list of user IDs to open a direct message channel with.
            
        Returns:
            channel_id (str): The channel ID of the newly opened direct message channel.
        """
        endpoint = 'https://slack.com/api/conversations.open'
        variables = urlencode({'users':user_ids})
        variables = variables.encode('ascii')

        request = Request(endpoint, headers=self._headers, data=variables)
        with urlopen(request) as response:
            data = json.loads(response.read().decode('utf8'))

        app.logger.info("Channel Data: " + json.dumps(data))
        
        channel_id = data['channel']['id']

        return channel_id
    
    def add_reaction(self, message, reaction='taco'):
        """
        Adds a reaction to a message.
        
        Args:
            message (str): The message to react to.
            reaction (str): The reaction to add.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        endpoint = 'https://slack.com/api/reactions.add'
        data = {
            "channel": message['event']['channel'],
            "timestamp": message['event']['ts'],
            "name": reaction
        }
        variables = urlencode(data)
        variables = variables.encode('ascii')
        request = Request(endpoint, headers=self._headers, data=variables)
        with urlopen(request) as response:
            data = json.loads(response.read().decode('utf8'))

        return data
    
    def send_message(self, message):
        """
        Send a message to a channel or direct message
        
        Args:
            message (dict): A message object
        """
        endpoint = 'https://slack.com/api/chat.postMessage'
        variables = urlencode(message)
        variables = variables.encode('ascii')
        
        request = Request(endpoint, headers=self._headers, data=variables)
        with urlopen(request) as response:
            data = json.loads(response.read().decode('utf8'))
            
        return data

class SlackEventHandler(object):
    def __init__(self, token):
        self._api = SlackApi(token)
        self.quotes = get_star_wars_quote()

    def send_message(self, message):
        """
        Send a message to a channel
        
        Args:
            message (dict): A message to send to a channel
            
        Returns:
            dict: The response from the Slack API
        """
        self._api.send_message(message)

    def mention_parser(self, request):
        """
        Parse app_mention events from Slack and return a message to send to the channel

        Args:
            request (dict): The request from Slack

        Returns:
            dict: A message body sent to the channel
        """
        bot_id = self._api.getCurrentBotInfo()
        bot_info = self._api.getBotInfo(bot_id=bot_id['bot_id'])
        app.logger.debug(json.dumps(bot_info))
        message = {"channel": request['event']['channel']}

        try:
            if 'help' in request['event']['text']:
                app.logger.info('Help me requested')
                help_message = [
                    f"@{bot_info['name']} quote: Get random Star Wars quotes."
                ]
                message['text'] = "\n".join(help_message)
            elif 'quote' in request['event']['text']:
                app.logger.info('Quotes requested')
                message['text'] = f"> {self.quotes['content']}"

            else:
                message['text'] = f"Good heavens. I didn't understand what you said.\n\nFor help, type `@{bot_info['bot']['name']} help`"
            
            app.logger.info(json.dumps(message))
            return message

        except Exception as e:
            app.logger.debug(f"Received message from user id {request['event']['user']}")
            app.logger.error(f"Unable to parse message: {e}")

            message['text'] = "R2! We're doomed! (Something went wrong. Please try again.)"
            return message

