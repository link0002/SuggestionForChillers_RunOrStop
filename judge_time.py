import datetime
import datetime
import logging

def judge_time(now_time, semSettings):
    '''

    :param now_time: 当前时间
    :param semSettings: 冷站需求时间
    :return: 当天的开机需求时刻
    datetime_start
    datetime_end
    '''
    now_time_str = now_time.strftime('%Y-%m-%d %H:%M:%S')
    datetime_start = None
    datetime_end = None
    week_C = now_time.weekday() + 1 # datetime的周机制（0-6）和Cycle不同
    if len(semSettings)==1:
        semSettings.append(semSettings[0])
    try:
        if semSettings[0]['Effect_begin_time'] < semSettings[1]['Effect_begin_time']:
            dic_min = semSettings[0]
            dic_max = semSettings[1]
        else:
            dic_min = semSettings[1]
            dic_max = semSettings[0]

        if now_time_str >= dic_max['Effect_begin_time']:
            if week_C in dic_max['Cycle']:
                time_start, time_end= dic_max["Time_interval"][0], dic_max["Time_interval"][1]
                if time_end=='24:00':
                    time_end = '23:59'
                datetime_start = now_time_str[:-8] + time_start + ':00'

                datetime_end = now_time_str[:-8] + time_end + ':00'

        else:
            if week_C in dic_min['Cycle']:
                time_start, time_end = dic_min["Time_interval"][0], dic_min["Time_interval"][1]
                if time_end=='24:00':
                    time_end = '23:59'
                datetime_start = now_time_str[:-8] + time_start + ':00'

                datetime_end = now_time_str[:-8] + time_end + ':00'

        # datetime_start = datetime.datetime.strptime(datetime_start, '%Y-%m-%d %H:%M:%S')
        # datetime_end = datetime.datetime.strptime(datetime_end, '%Y-%m-%d %H:%M:%S')

    except Exception as e:
        logging.info('-----judge_time error!-----')
        logging.error(e)
        raise e
    return datetime_start, datetime_end

# if __name__ == "__main__":
#     now_time = datetime.datetime.now()
#     print(now_time)
#     semSettings = [{
#         "Effect_begin_time": "2019-07-19 00:00:00",
#         "Time_interval": ["06:00", "24:00"],
#         "Cycle": [1, 2, 3, 4, 5, 6, 7]}, {
# 		"Effect_begin_time": "2019-07-15 00:00:00",
# 		"Time_interval": ["01:00", "24:00"],
# 		"Cycle": [1, 2, 3, 4, 5, 6, 7]
# 	}]
#     time1, time2 = judge_time(now_time, semSettings)
#     print(time1, time2)
#     print(type(time2))