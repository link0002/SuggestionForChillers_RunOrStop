from get_data import get_data_fromMQ, get_data_from_redis
from CommunicationConfig import *
from dealing_and_analysis import dealing_data, analysis, send_data_to_RabbitMQ


def main_function():

    now_time, now_time_str = Now_time()
    print('当前时间是:'.center(50, '-'))
    print(now_time)

    mq_message = get_data_fromMQ()

    Redis_data = get_data_from_redis(mq_message)

    asId, df_now, df_now_1, df_now_2 = dealing_data(Redis_data)

    list_out = analysis(asId, df_now, df_now_1, df_now_2)

    # send_data_to_RabbitMQ(list_out)


if __name__ == '__main__':

    main_function()
