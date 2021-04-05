from CommunicationConfig import *
import pika
import logging


class RabbitMQ(object):
    def __init__(self, queue_name, routing_key):
        """
        初始化参数:
        用户名，密码，ip，端口，交换机，交换机类型，队列名称，路由key
        """
        self._host = HOST_RM  # broker IP
        self._port = PORT_RM  # broker port
        # self._vhost = vhost  # vhost
        self._exchange = EXCHANGE
        self._exchange_type = EXCHANGE_TYPE
        self._queue_name = queue_name
        self._routing_key = routing_key
        self._credentials = pika.PlainCredentials(USERNAME_RM, PASSWORD_RM)

    def connect(self):
        # 连接RabbitMQ的参数对象
        parameter = pika.ConnectionParameters(self._host, self._port,
                                              credentials=self._credentials)

        self.connection = pika.BlockingConnection(parameter)  # 建立连接

        self.channel = self.connection.channel()

    def declare_exchange(self):
        """
        声明交换机
        :return: None
        """
        self.channel.exchange_declare(exchange=self._exchange,
                                      exchange_type=self._exchange_type,
                                      durable=True)

    def declare_queue(self):
        """
        声明队列
        :return: None
        """
        self.declare_queue_result = self.channel.queue_declare(queue=self._queue_name,
                                                          durable=True)

    def bind_queue(self):
        """
        将交换机下的队列名与路由key绑定起来
        :return: None
        """
        self.channel.queue_bind(exchange=self._exchange,
                                queue=self._queue_name,
                                routing_key=self._routing_key)

    def publish(self, body):
        """
        发布消息
        :return: None
        """
        self.channel.basic_publish(exchange=self._exchange,
                                   routing_key=self._routing_key,
                                   body=body)

    def consume(self):
        """
        消费信息，先判断队列中是否有消息，如果无，过，如有，则消费掉队列中的所有消息
        :return: None
        """

        message_count = self.declare_queue_result.method.message_count

        if message_count == 0:
            raise ValueError('No messages in Rabbitmq !'.center(50, '*'))
        else:
            for method, properties, body in self.channel.consume(self._queue_name):
                self.channel.basic_ack(method.delivery_tag, multiple=False)
                if method.delivery_tag == message_count:
                    message_get = body.decode()
                    break
        return message_get

    def connection_close(self):
        self.connection.close()


# if __name__=='__main__':
#
#     from CommunicationConfig import *
#
#     queue_name = QUEUE_NAME_GET
#     routing_key = ROUTING_KEY_GET
#     mq = RabbitMQ(queue_name, routing_key)
#     mq.connect()
#     mq.declare_exchange()
#     mq.declare_queue()
#     mq.bind_queue()
#     mess = mq.consume()
#     print(mess)
#     # i = 0
#     # while i < 10:
#     #     i = i + 1
#     #     mq.publish('我是第%s条消息'% i)
#     mq.connection_close()
