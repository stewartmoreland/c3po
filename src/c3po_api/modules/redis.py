from redis import StrictRedis, RedisError

from flask import current_app as app

class RedisIndex(object):
    def __init__(self, db_index=0):
        self.db = StrictRedis(host=app.config['REDIS_HOST'],
                        port=app.config['REDIS_PORT'],
                        password=app.config['REDIS_PASS'],
                        db=db_index)

    def getKey(self, item_key):
        item = self.db.get(name=item_key)
        item = item.decode('utf-8')

        return item

    def setKey(self, item_key, value):
        self.db.set(name=item_key,value=value)

    def setHashFromDict(self, item_key, item_dict):
        for key, value in item_dict:
            self.db.hset(item_key, key, value)

    def getHashToDict(self, item_key):
        item_dict = self.db.hgetall(item_key)
        
        for bytes_key, value in item_dict:
            key = bytes_key.decode('utf-8')
            item_dict[key] = item_dict.pop[bytes_key]
            item_dict[key] = value.decode('utf-8')

        return item_dict

