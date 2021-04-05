from CommunicationConfig import *
import redis
import datetime
import json


class RedisConnection():

    def __init__(self):
        """
        初始化参数:
        ip，端口,密码
        """
        self.host = REDIS_HOST
        self.port = REDIS_PORT
        self.password = REDIS_PASS
        self.date = str(datetime.datetime.now().strftime("%Y-%m-%d"))
        # self.time_now = "2019-04-26"

    def connect(self):

        self.pool = redis.ConnectionPool(host=self.host, port=self.port, password=self.password, decode_responses=True)
        self.connection = redis.Redis(connection_pool=self.pool)

    def get_data(self, key):

        data = []
        self.keys = self.connection.keys(key)

        for i in self.keys:
            tmp = json.loads(self.connection.get(i))
            data.append(tmp)

        if data == []:
            raise ValueError('Key error or No datas in Redis!'.center(50, '*'))

        else:
            return data

    def set_value(self, key, value):

        self.connection.set(key, value)
