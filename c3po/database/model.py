#! /usr/bin/env python
from sqlalchemy import Column, Integer, String, ForeignKey
from c3po.database import Base


class User(Base):
    __tablename__ = 'users'

    slack_id = Column(String(16), primary_key=True)
    user_name = Column(String(64))
    slack_subscription = Column(String(32))
    full_name = Column(String(64), nullable=True)
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
