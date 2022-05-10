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
        if not token:
            raise EnvironmentError()
        self._headers = {}
        self._headers["Authorization"] = "Bearer {}".format(token)

    def get_all_users(self):
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
        endpoint = 'https://slack.com/api/auth.test'
        self._headers["Content-Type"] = "application/x-www-form-urlencoded"
        request = Request(endpoint, headers=self._headers)
        with urlopen(request) as response:
            data = json.loads(response.read().decode('utf8'))
        return data

    def get_bot_info(self, bot_id):
        endpoint = 'https://slack.com/api/bots.info'
        endpoint = endpoint + '?bot={}'.format(bot_id)
        self._headers["Content-Type"] = "application/x-www-form-urlencoded"
        request = Request(endpoint, headers=self._headers)
        with urlopen(request) as response:
            data = json.loads(response.read().decode('utf8'))
        return data

    def get_user_info(self, user_id):
        endpoint = 'https://slack.com/api/users.info'
        variables = urlencode({'user':user_id})
        variables = variables.encode('ascii')
        user_data = {}

        request = Request(endpoint, headers=self._headers, data=variables)
        with urlopen(request) as response:
            user_data = json.loads(response.read().decode('utf8'))
        
        return user_data

    def get_conversation_info(self, user_id):
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
        except:
            app.logger.error(f'Unable to find channel {channel_name}. If this is a private channel, try adding the bot user to the channel to make it visible.')

    def get_channel_list(self):
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
        self._api.send_message(message)

    def mention_parser(self, request):
        bot_id = self._api.getCurrentBotInfo()
        bot_info = self._api.getBotInfo(bot_id=bot_id['bot_id'])
        app.logger.debug(json.dumps(bot_info))
        message = {"channel": request['event']['channel']}

        try:
            if 'help me' in request['event']['text']:
                app.logger.info('Help me requested')
                help_message = [
                    f"@{bot_info['name']} quotes: Get random Star Wars quotes."
                ]
                message['text'] = "\n".join(help_message)
            elif 'quotes' in request['event']['text']:
                app.logger.info('Quotes requested')
                message['text'] = f"> {self.quotes['content']}"

            else:
                message['text'] = f"Good heavens. I didn't understand what you said.\n\nFor help, type `@{bot_info['bot']['name']} help me`"
            
            app.logger.info(json.dumps(message))
            return message

        except Exception as e:
            app.logger.debug(f"Received message from user id {request['event']['user']}")
            app.logger.error("Unable to parse message.")
            app.logger.error(e)

            message['text'] = "Oops. Something went wrong."
            return message

