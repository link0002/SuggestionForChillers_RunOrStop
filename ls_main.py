#!/usr/bin/env python
# -*- coding:utf-8 -*-
from CommunicationConfig import configs
import pandas as pd
import datetime
import requests
import json
pd.set_option("display.max_columns", None)
from sql import PymysqlPool

def timestamp_to_datetime(timestamp_list, ds_type):

    if ds_type == 'datetime':
        datetime_list = []
        for cur_timestamp in timestamp_list:
            cur_datetime = datetime.datetime.combine(cur_timestamp.date(), cur_timestamp.time())
            datetime_list.append(cur_datetime)
        return datetime_list
    else:
        date_list = []
        for cur_timestamp in timestamp_list:
            cur_date = cur_timestamp.date()
            date_list.append(cur_date)
        return date_list


def search_and_deal(meter_id, start_time, end_time, mysql):

    sql_meter_data = "SELECT date_time as ds, ygglz as y FROM em_elec_meter_data " \
                     "WHERE meter_id = {} and date_time between '{}' and '{}'".format(meter_id, start_time, end_time)
    df = mysql.pandas_read(sql_meter_data)
    df.drop_duplicates("ds",inplace=True)
    df['ds'] = pd.to_datetime(df.ds)
    df.set_index("ds", inplace=True)
    df.fillna(method='backfill', inplace=True)
    df = df.resample('1h', limit=2).bfill()
    df.dropna(inplace=True)
    df.y = df.y.apply(lambda x:float(x))
    return df


def get_data(start_time, end_time, as_id):

    mysql_meter = PymysqlPool(configs["database_meter_config"])
    sql_chiller = "SELECT meter_id FROM watcooler_meter WHERE as_id = {}".format(as_id)
    chiller_id_list = mysql_meter.pandas_read(sql_chiller)['meter_id'].unique().tolist()  # 主机meter_id list
    equip_id_list = []  # 设备id_list
    mysql_entity = PymysqlPool(configs["database_entity_config"])
    for meter_id in chiller_id_list:  # 查询与主机关联的电表
        sql_chiller_meter = "SELECT equip_id FROM em_equip_meter WHERE meter_id = {}".format(meter_id)
        equip_id_list.append(mysql_entity.getOne(sql_chiller_meter)["equip_id"])
    elec_meter_list = []  # 电表id_list
    for equip_id in equip_id_list:
        sql_elec_meter = "SELECT meter_id FROM em_equip_meter WHERE equip_id = {} AND relate_type=1".format(equip_id)
        elec_meter_list.append(mysql_entity.getOne(sql_elec_meter)["meter_id"])

    data_list = list(map(search_and_deal, elec_meter_list, [start_time] * len(elec_meter_list),
                         [end_time] * len(elec_meter_list), [mysql_meter]*len(elec_meter_list)))
    # if as_id == 1000043:
    #     data_list[0].y = data_list[0].y.apply(lambda x: x * 1.5)

    data_df = sum(data_list)
    mysql_entity.dispose()
    mysql_meter.dispose()

    return data_df


def fill(df):

    ds = df.index.tolist()
    ds = str(timestamp_to_datetime(ds, ds_type='datetime'))
    y = str(df.y.tolist())
    params = {'data_type': 2, 'freq': 'H', 'ds': ds, 'y': y}
    r = requests.post("http://47.112.119.36:48001/fill", data=params)
    try:
        df = pd.DataFrame(json.loads(r.text))
        df.ds = df.ds.apply(
            lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        print(r.text)
    finally:
        df.reset_index(inplace=True)
    return df


def normal(df):

    ds = df.ds.tolist()
    ds = str(timestamp_to_datetime(ds, ds_type='datetime'))
    y = str(df.y.tolist())
    params = {'freq': 'H', 'ds': ds, 'y': y, 'check_way': '1', 'k_std': '3'}
    r = requests.post("http://47.112.119.36:48001/normal", data=params)
    print(r.text)
    try:
        df = pd.DataFrame(json.loads(r.text))
        df.ds = df.ds.apply(
            lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    except:
        print(r.text)
    finally:
        df.reset_index(inplace=True)
    return df


def weather_data(params, start_time, end_time, predict_time):
    params_pass, params_future = params.copy(), params.copy()
    params_pass["startTime"], params_pass["endTime"] = start_time, end_time
    params_future["startTime"], params_future["endTime"] = end_time, predict_time
    r = requests.post("http://14.23.57.52:38207/weather/current/list", json=params_pass)
    text = json.dumps(json.loads(r.text))
    df_weather = pd.read_json(text)
    df_weather = df_weather[["dateTime", "tmp", "hum"]]
    df_weather.rename(columns={"dateTime": "date_time"}, inplace=True)
    r = requests.post("http://14.23.57.52:38207/weather/forecasthour/list", json=params_future)
    text = json.dumps(json.loads(r.text))
    weather_future = pd.read_json(text)
    weather_future = weather_future[["dateTime", "tmp", "hum"]]
    weather_future.rename(columns={"dateTime": "date_time"}, inplace=True)
    weather_future.dropna(inplace=True)
    if len(weather_future) < 25:
        weather_future = df_weather[-25:].copy()
        weather_future.reset_index(drop=True, inplace=True)
        weather_future.date_time = weather_future.apply(lambda x:x.date_time + pd.Timedelta(hours=1), axis=1)
    return df_weather, weather_future


def sis(df, weather_df):

    df_conbine = pd.concat([df, weather_df], axis=1)

    df_conbine.dropna(inplace=True)
    ds = df_conbine.ds.tolist()
    ds = str(timestamp_to_datetime(ds, ds_type='datetime'))
    y = str(df_conbine.y.tolist())
    # weather_ds = weather_df.date_time.tolist()
    hum = str(df_conbine.hum.tolist())
    tmp = str(df_conbine.tmp.tolist())

    params_sis = {
        'freq': 'H',
        'ds': ds,
        'y': y,
        'weather_ds': ds,
        'hum': hum,
        'tmp': tmp,

    }
    r_sis = requests.post("http://47.112.119.36:48002/sis", data=params_sis)
    print(r_sis.text)
    return r_sis.text


def build(df_weather, df, alg_name, start_time, end_time, weather_future, r_sis):
    ds = df.ds.tolist()
    ds = str(timestamp_to_datetime(ds, ds_type='datetime'))
    weather_ds = df_weather.date_time.tolist() + weather_future.date_time.tolist()
    weather_ds = str(timestamp_to_datetime(weather_ds, ds_type='datetime'))
    y = str(df.y.tolist())
    hum = str(df_weather.hum.tolist() + weather_future.hum.tolist())
    tmp = str(df_weather.tmp.tolist() + weather_future.tmp.tolist())
    model_param = {'lgbm':{
                            'subsample': [0.85],
                            'num_leaves': [64],
                            'n_estimators': [300],
                            'min_split_gain': [0.1],
                            'learning_rate': [0.01],
                            'colsample_bytree': [0.95]
                            }}
    print('model parameter', str(model_param))
    params = {
        "freq": "H",
        "start_time": start_time,
        "end_time": end_time,
        "algs": str([alg_name]),
        "ds": ds,
        "y": y,
        "weather_ds": weather_ds,
        "hum": hum,
        "tmp": tmp,
        # "holiday_ratio":1.0,
        "sis_result": r_sis,
        "model_param": str(model_param)
    }
    r = requests.post("http://47.112.119.36:48003/pred", data=params)
    # r = requests.post("http://127.0.0.1:5000/pred", data=params)  # 本地
    predict = json.loads(r.text)[alg_name]['pred_list']
    datetime = json.loads(r.text)['ds']
    result = {'predict':predict, 'datetime':datetime}
    return result


def predict(as_id, params_city):
    alg_name = 'lgbm'
    # ====================================================================================放在阿里云hours=8
    time_now = datetime.datetime.now() + datetime.timedelta(hours=0)
    start_time = (time_now - datetime.timedelta(days=30)).strftime("%Y-%m-%d %H") + ":00:00"
    end_time = (time_now).strftime("%Y-%m-%d %H") + ":00:00"
    predict_time = (time_now + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H") + ":00:00"
    data_df = get_data(start_time, end_time, as_id)
    print('过去30天电量负荷数据:'.center(50, '-'))
    print(data_df)
    data_df = fill(data_df, )
    data_df = normal(data_df)
    df_weather, weather_future = weather_data(params_city, start_time, end_time, predict_time)
    r_sis = sis(data_df, df_weather)
    r_sis = json.loads(r_sis)
    r_sis["holiday"] = 1.0
    r_sis["holiday_ratio"] = 1.0
    r_sis["24_holiday_curve"] = []
    r_sis = json.dumps(r_sis)
    predict = build(df_weather, data_df, alg_name, end_time, predict_time, weather_future, r_sis)
    print('未来24小时负荷预测结果:'.center(50, '-'))
    print(predict)
    return predict


# if __name__ == '__main__':
#     params_city = {
#         "provId": 5,
#         "cityId": 30,
#         "countyId": 356
#     }
#     as_id = 1000043
#     result = predict(as_id, params_city)
