from CommunicationConfig import *
from MQ_connection import RabbitMQ

from Redis_connection import RedisConnection
import json


def get_data_fromMQ():
    '''
    :return: 返回rabbitmq的最新消息，str格式
    '''
    queue_name = QUEUE_NAME_GET
    routing_key = ROUTING_KEY_GET
    mq = RabbitMQ(queue_name, routing_key)
    mq.connect()
    mq.declare_exchange()
    mq.declare_queue()
    mq.bind_queue()
    mq_mess = mq.consume()
    mq.connection_close()
    print('messages from MQ:'.center(50, '-'))
    print(mq_mess)

    return mq_mess


def get_data_from_redis(mq_mess):
    """
    从redis取出数据
    :param： mq_mess
    :return: Redis_data dict格式
    """
    R = RedisConnection()
    R.connect()
    mq_mess = json.loads(mq_mess)
    for i in mq_mess['datas']:
        Chiller_ID = i['Chiller_ID']
        i["chiller_data"] = R.get_data("yqRecordScheduleKey:*{}*".format(Chiller_ID))

    Redis_data = mq_mess
    print('messages from Redis:'.center(50, '-'))
    print(Redis_data)

    return Redis_data

#
# if __name__=='__main__':
#
#     mq_message = get_data_fromMQ()
#
#     Redis_data = get_data_from_redis(mq_message)

