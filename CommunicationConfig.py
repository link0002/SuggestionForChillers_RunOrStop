import datetime
from configs_files.configs_for_prod import configs

ROOT_PATH = configs["root_path"]  # 根路径

# 与rabbitmq通讯相关的参数设置
USERNAME_RM = configs["rabbitmq_config"]["username"]  # 用户名
PASSWORD_RM = configs["rabbitmq_config"]["password"]  # 密码
HOST_RM = configs["rabbitmq_config"]["host"]  # ip
PORT_RM = int(configs["rabbitmq_config"]["port"])  # 端口

EXCHANGE = configs["rabbitmq_config"]["exchange"]  # 交换机名称
EXCHANGE_TYPE = configs["rabbitmq_config"]["exchange_type"]  # 交换机方式

QUEUE_NAME_GET = configs["rabbitmq_config"]["queue_name_get"]  # 获取数据的队列
ROUTING_KEY_GET = configs["rabbitmq_config"]["routing_key_get"]  # 获取数据的routingkey

QUEUE_NAME_SEND = configs["rabbitmq_config"]["queue_name_send"]  # 发送数据的队列
ROUTING_KEY_SEND = configs["rabbitmq_config"]["routing_key_send"]  # 发送数据的routingkey

# 和Redis通讯相关的参数设置
REDIS_HOST = configs["redis_config"]["redis_host"]  # redis ip
REDIS_PORT = int(configs["redis_config"]["redis_port"])  # redis port
REDIS_PASS = configs["redis_config"]["redis_pass"]  # redis password

# 与数据通讯相关的设置
configs["database_meter_config"]['port'] = int(configs["database_meter_config"]['port'])
configs["database_entity_config"]['port'] = int(configs["database_entity_config"]['port'])

# 全局时间
TIME_NOW = datetime.datetime.now() + datetime.timedelta(hours=0)


def Now_time():

    # 本地运行hours = 0,放在阿里云hours=8--------------------------<<<<<<<-----------
    now_time = TIME_NOW
    now_time_str = now_time.strftime('%Y-%m-%d %H:%M:%S')
    now_time = datetime.datetime.strptime(now_time_str, '%Y-%m-%d %H:%M:%S')

    return now_time, now_time_str

# for test,本地连接数据库
# configs["database_meter_config"]['host'] = "rm-wz9mrghoq4vi49844jo.mysql.rds.aliyuncs.com"
# configs["database_meter_config"]['port'] = 3306
# configs["database_meter_config"]['user'] = "readonly"
# configs["database_meter_config"]['passwd'] = "readOnLy020"
#
# configs["database_entity_config"]['host'] = "rm-wz9mrghoq4vi49844jo.mysql.rds.aliyuncs.com"
# configs["database_entity_config"]['port'] = 3306
# configs["database_entity_config"]['user'] = "readonly"
# configs["database_entity_config"]['passwd'] = "readOnLy020"
