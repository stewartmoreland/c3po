#! /usr/bin/env python
from sqlalchemy import Column, Integer, String, ForeignKey
from c3po.database import Base


class User(Base):
    __tablename__ = 'c3po_users'

    id = Column(String(16), primary_key=True)
    user_name = Column(String(64))
    full_name = Column(String(64), nullable=True)
    email = Column(String(64), nullable=True)
    team_id = Column(String(64))
    slack_user_id = Column(String(16), nullable=True)
    slack_subscription = Column(String(32))
    github_oauth_token = Column(String(64), nullable=True)
    gitlab_oauth_token = Column(String(64), nullable=True)

    def __init__(self, slack_id=None, user_name=None, slack_subscription=None, full_name=None, github_oauth_token=None, gitlab_oauth_token=None):
        self.slack_id = slack_id
        self.user_name = user_name
        self.slack_subscription = slack_subscription
        self.full_name = full_name
        self.github_oauth_token = github_oauth_token
        self.gitlab_oauth_token = gitlab_oauth_token

    def __repr__(self):
        return self


class StarWarsQuotes(Base):
    __tablename__ = 'starwarsquotes'

    id = Column(Integer, primary_key=True)
    quote = Column(String(256))
    character = Column(String(64))
    movie = Column(String(64))

    def __init__(self, quote=None, character=None, movie=None):
        self.quote = quote
        self.character = character
        self.movie = movie

    def __repr__(self):
        return self
    
    def _to_dict(self):
        return {
            'quote': self.quote,
            'character': self.character,
            'movie': self.movie
        }
