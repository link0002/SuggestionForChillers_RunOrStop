import pandas as pd
import numpy as np
import json
from my_M import my_Main
from get_data import get_data_fromMQ, get_data_from_redis
from MQ_connection import RabbitMQ
from CommunicationConfig import *
pd.set_option("display.max_columns", None)


def check_None_Balank_data(df):

    asId = df.iloc[0]['asId']
    true_counts = df.iloc[0].isin(['', np.nan]).sum()  #  空值的数量

    if true_counts == 0:
        print('冷机%s数据完整' % df.iloc[0]['Chiller_ID'])
        return None
    else:
        print('冷机%s数据不完整！！！' % df.iloc[0]['Chiller_ID'])
        return asId


def check_data_delayoffline(df):

    now_time, now_time_str = Now_time()

    last_time = datetime.datetime.strptime(df.iloc[0]['Date_time'], '%Y-%m-%d %H:%M:%S')
    asId = df.iloc[0]['asId']
    Chiller_ID = df.iloc[0]['Chiller_ID']

    if last_time < now_time - datetime.timedelta(minutes=20):  # 如果数据延迟了20min
        print('冷站：%s\nchiller:%s data delay!\nLast_time is:%s\nNow is: %s' % (asId, Chiller_ID, last_time, now_time))
        return asId
    else:
        return None


def dealing_data(Redis_data):

    asId = []
    asId_sub = []
    df_now = pd.DataFrame()
    df_now_1 = pd.DataFrame()
    df_now_2 = pd.DataFrame()

    # 对每台冷机
    print('冷机数据完整性检查:'.center(50, '-'))

    for i in Redis_data['datas']:

        asId.append(i['asId'])

        # 每台冷机的参数(大约有6条数据)
        data_a_chiller_alltime = i['chiller_data']

        df = pd.DataFrame(data_a_chiller_alltime)
        df = df.sort_values(by='Date_time', ascending=False)
        df = df.iloc[:4]  # 每台冷机的前4条数据

        df['provId'] = i['provId']
        df['cityId'] = i['cityId']
        df['countyId'] = i['countyId']

        asId_sub.append(check_None_Balank_data(df))
        asId_sub.append(check_data_delayoffline(df))

        df_now = df_now.append(df.iloc[:1])  # 第1条记录(最近时刻的采集数据)：所有冷机
        df_now_1 = df_now_1.append(df.iloc[1:2])  # 第2条记录：所有冷机
        df_now_2 = df_now_2.append(df.iloc[2:3])  # 第3条记录：所有冷机

    asId = list(set(asId) - set(asId_sub))  # 冷站ID的列表(数据正常的)

    df_now[['Capacity', 'Power', 'COP']] = df_now[['Capacity', 'Power', 'COP']].apply(pd.to_numeric)
    df_now_1[['Capacity', 'Power', 'COP']] = df_now_1[['Capacity', 'Power', 'COP']].apply(pd.to_numeric)
    df_now_2[['Capacity', 'Power', 'COP']] = df_now_2[['Capacity', 'Power', 'COP']].apply(pd.to_numeric)

    df_now = df_now.reindex(['provId', 'cityId', 'countyId', 'Date_time', 'entityId', 'asId', 'semSettings',
                             'Chiller_ID',  'Power', 'Capacity', 'COP', 'Run_time', 'Power_t', 'Load_t', 'T_set',
                             'T_chilled'], axis=1)

    df_now_1 = df_now_1.reindex(['provId', 'cityId', 'countyId', 'Date_time', 'entityId', 'asId', 'semSettings',
                                 'Chiller_ID', 'Power', 'Capacity', 'COP', 'Run_time', 'Power_t', 'Load_t', 'T_set',
                                 'T_chilled'], axis=1)

    df_now_2 = df_now_2.reindex(['provId', 'cityId', 'countyId', 'Date_time', 'entityId', 'asId', 'semSettings',
                                 'Chiller_ID', 'Power', 'Capacity', 'COP', 'Run_time', 'Power_t', 'Load_t', 'T_set',
                                 'T_chilled'], axis=1)

    print('最近3条记录:'.center(50, '-'))
    print('(1)正常运行的冷站：%s' % asId)
    print('(2)所有冷机最近时刻记录：')
    print(df_now)
    print('(3)所有冷机最近上1条时刻记录：')
    print(df_now_1)
    print('(4)所有冷机最近上2条时刻记录：')
    print(df_now_2)

    return asId, df_now, df_now_1, df_now_2


def analysis(asId, df_now, df_now_1, df_now_2, future_hours=4):  # 一旦要开关机就预测未来4个小时的负荷

    list_out = []

    for i in asId:  # 对每一个冷站进行处理

        data_t = df_now[df_now['asId'] == i]
        data_t_1 = df_now_1[df_now_1['asId'] == i]
        data_t_2 = df_now_2[df_now_2['asId'] == i]

        data_t = data_t.sort_values(by='Power')
        data_t_1 = data_t_1.sort_values(by='Power')
        data_t_2 = data_t_2.sort_values(by='Power')

        data_t.index = np.arange(len(data_t))
        data_t_1.index = np.arange(len(data_t_1))
        data_t_2.index = np.arange(len(data_t_2))

        semSettings = data_t['semSettings'][0]  # 该冷站的需求时间

        output_data = my_Main(data_t, data_t_1, data_t_2, semSettings, future_hours)
        output_data = output_data.rename(columns={'Chiller_ID': 'chillerId', 'suggestion_state': 'suggestionState'})

        output_data_need = output_data[['entityId', 'asId', 'chillerId', 'T_chilled_predict', 'power_rate_t',
                                        'suggestionState', 'dateTime']]

        print(('冷站：%s建议状态' % i).center(50, '-'))
        print(output_data_need)

        output_data_need = output_data_need.to_json(orient='records')
        output_data_need = json.loads(output_data_need)
        list_out = list_out + output_data_need
        # list_out = list_out.append(output_data_need)

    list_out = json.dumps(list_out)

    return list_out


def send_data_to_RabbitMQ(list_out):

    queue_name = QUEUE_NAME_SEND
    routing_key = ROUTING_KEY_SEND
    rabbitmq_connection_send = RabbitMQ(queue_name, routing_key)  # 实例化
    rabbitmq_connection_send.connect()  # 建立连接
    rabbitmq_connection_send.declare_exchange()  # 声明交换机
    rabbitmq_connection_send.declare_queue()  # 声明队列
    rabbitmq_connection_send.bind_queue()  # 绑定队列
    rabbitmq_connection_send.publish(list_out)
    rabbitmq_connection_send.connection_close()  # 关闭连接
    print('messages:%s' % list_out)
    print('Message Transfer Finished'.center(50, '-'))

#
# if __name__ == '__main__':
#
#     mq_message = get_data_fromMQ()
#     Redis_data = get_data_from_redis(mq_message)
#     now_time, now_time_str = Now_time()
#     print('当前时间是:'.center(50, '-'))
#     print(now_time)
#
#     asId, df_now, df_now_1, df_now_2 = dealing_data(Redis_data)
#     list_out = analysis(asId, df_now, df_now_1, df_now_2)
