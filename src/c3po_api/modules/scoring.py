#!/usr/bin/env python3
from flask import current_app as app
import json

from sqlalchemy.sql.elements import Null

def get_user_score(slack_id):
    from c3po_api.database import db_session
    from c3po_api.database.model import Score

    user = db_session.query(Score).filter(Score.slack_id == slack_id).first()

    return user

def add_point_to_user(recipient_id, sender_id):
    from c3po_api.database import db_session
    from c3po_api.database.model import Score
    import re

    recipient_id = re.sub('[@<!#$>]', '', recipient_id)

    if Score.query.filter(Score.slack_id == recipient_id).first() is None:
        recipient = Score(slack_id=recipient_id,score=0,given=0,bank=5)
    else:
        recipient = Score.query.filter(Score.slack_id == recipient_id).first()
    
    if Score.query.filter(Score.slack_id == sender_id).first() is None:
        sender = Score(slack_id=sender_id,score=0,given=0,bank=5)
    else:
        sender = Score.query.filter(Score.slack_id == sender_id).first()

    recipient.score = recipient.score + 1
    db_session.add(recipient)
    db_session.commit()

    sender.bank = sender.bank - 1
    sender.given = sender.given + 1
    db_session.add(sender)
    db_session.commit()

def get_leaderboard():
    from c3po_api.database.model import Score
    request = Score.query.order_by(Score.score.desc()).limit(10)
    response = str()

    for user in request:
        response = response + f"<@{user.slack_id}> - {user.score}\n"

    return response
