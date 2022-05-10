#!/usr/bin/env python3
from flask import current_app as app

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from slack_sdk.oauth.installation_store.sqlalchemy import SQLAlchemyInstallationStore
from slack_sdk.oauth.state_store.sqlalchemy import SQLAlchemyOAuthStateStore

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

installation_store = SQLAlchemyInstallationStore(client_id=app.config['SLACK_CLIENT_ID'], engine=db_session.bind, logger=app.logger)
state_store = SQLAlchemyOAuthStateStore(expiration_seconds=300, engine=db_session.bind, logger=app.logger)

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    Base.metadata.create_all(bind=engine)
    try:
        engine.execute("select count(*) from slack_bots")
    except Exception as e:
        app.logger.info(f"Initializing Slack Oauth tables: {e}")
        installation_store.metadata.create_all(bind=engine)
        state_store.metadata.create_all(bind=engine)
