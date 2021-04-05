import datetime
import logging

from chiller_state import chillers_state
from ls_main import predict
from chiller_combins_suggestion import chiller_combins_suggestion
from judge_time import judge_time
from CommunicationConfig import Now_time


def my_Main(data_t, data_t_1, data_t_2, semSettings, future_hours=4):
    # future_hours 是指预测到的未来4个小时的最大负荷，根据这个来判断冷机组合，semSettings为需求时间

    now_time, now_time_str = Now_time()

    data_t['dateTime'] = now_time_str[:-3] + ':00'

    # 冷站，城市天气，预测负荷
    as_id = data_t.iloc[0]['asId']
    params_city = {
        "provId": int(data_t.iloc[0]['provId']),
        "cityId": int(data_t.iloc[0]['cityId']),
        "countyId": 0
    }

    value, data_t = chillers_state(data_t, data_t_1, data_t_2)

    if value == None:

        # 不执行操作，维持上一条信息状态，也就是当前冷机组合状态。
        # data_t加一列，给出当前的冷机组合建议
        datetime_start, datetime_end = judge_time(now_time, semSettings) # 当天的需求时间
        datetime_start_1, datetime_end_1 = judge_time(now_time + datetime.timedelta(days=1), semSettings)  # 第二天的需求时间

        datetime_end_t = datetime.datetime.strptime(datetime_end, '%Y-%m-%d %H:%M:%S')
        datetime_start_1 = datetime.datetime.strptime(datetime_start_1, '%Y-%m-%d %H:%M:%S')

        d_time_30min = datetime_end_t - datetime.timedelta(minutes=30)

        if (d_time_30min < now_time) and (now_time < datetime_end_t) and (datetime_end - datetime_start_1 > datetime.timedelta(minutes=60)): # 仅在需求时间提前30min提醒关机
            data_t['suggestion_state'] = False
        else:
            data_t['suggestion_state'] = data_t['Load_t'] > 0 # 保持冷机状态

    elif value == 0:
        # datetime_start,datetime_end是当天冷站运行的需求时间
        # 当前时间，如果在配置的开机时刻前1H内，应该提醒去开机了。
        datetime_start, datetime_end = judge_time(now_time, semSettings)  # 当天的需求时间
        datetime_start_t = datetime.datetime.strptime(datetime_start, '%Y-%m-%d %H:%M:%S')
        d_time_1H = datetime_start_t - datetime.timedelta(hours=1)

        if (d_time_1H < now_time) and (now_time < datetime_start_t):  # 仅在需求时间提前1H进行负荷预测,给出开机组合

            #  --------运行预测函数，得到冷机开机组合
            result = predict(as_id, params_city)
            series_load = result['predict']
            load = max(series_load[:future_hours])
            # print(load)
            data_t = chiller_combins_suggestion(data_t, max_load_in3H=load)
        # if datetime_start < now_time_str: #当天需求时间小于当前时间，也就是时间过了,那应该预测第二天的开机时间

        # 当前时间，如果在配置的开机时间段范围内（就不执行，维持冷机组合状态，不骚扰用户），以及其他时间段，应该维持冷机关机状态
        else:
            data_t['suggestion_state'] = False  # 逻辑表达式

    else:
        # 此时冷量偏大或者偏小，重新执行预测，重新给出预测的冷机组合
        result = predict(as_id, params_city)
        series_load = result['predict']
        load = max(series_load[:future_hours])
        # print(load)
        data_t = chiller_combins_suggestion(data_t, max_load_in3H=load)

    return data_t


if __name__ == "__main__":

    pass
