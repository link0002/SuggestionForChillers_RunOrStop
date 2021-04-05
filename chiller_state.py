import pandas as pd
import numpy as np
import logging
pd.set_option('display.max_columns', None)

# 冷机状态
def chillers_state(data_t, data_t_1, data_t_2):
    # 衡量当前组合是否应该增开冷机的指标
    T_chilled_predict = []
    # 衡量当前组合是否应该减少开机的指标（实际上是冷机的功率负载）
    power_rate_t = []

    for i in np.arange(len(data_t)):
        # 冷机的实时负载率
        Load_t = data_t.iloc[i]['Load_t']

        # 实时功率比额定功率
        power_rate = round(data_t.iloc[i]['Power_t'] / data_t.iloc[i]['Power'] * 100, 1)

        if Load_t < 2:  # 认为没开机
            T_chilled_predict.append(None)
            power_rate_t.append(None)
        else:
            temp_differ = data_t.iloc[i]['T_chilled'] - data_t.iloc[i]['T_set']
            temp_up_rate_in_delta = 0.3 * (data_t_1.iloc[i]['T_chilled'] - data_t_2.iloc[i]['T_chilled']) + 0.7 * (
                        data_t.iloc[i]['T_chilled'] - data_t_1.iloc[i]['T_chilled'])
            power_rate_t.append(power_rate)
            # 冷机的实时功率大于0.8倍的额定功率时：
            if Load_t > 80:
                # 当水温是上升的且设定温差大于3.5℃
                if (temp_up_rate_in_delta > 0.15) and (temp_differ >= 3.5):
                    T_chilled_predict.append(temp_up_rate_in_delta + temp_differ)  # 预计delta_T min后的出水温度与设定值温差
                else:
                    T_chilled_predict.append(temp_up_rate_in_delta)
            else:
                T_chilled_predict.append(temp_up_rate_in_delta)

    data_t['T_chilled_predict'] = T_chilled_predict
    data_t['power_rate_t'] = power_rate_t

    # 默认,不做操作,给个假设默认值None
    Tips = '冷机组合:%s处于默认状态（正常运行）' % data_t.iloc[0]['asId']
    value = None
    # 假如没有开冷机
    if data_t[data_t['Load_t'] > 0].empty:
        Tips = '冷机组合:%s处于关机状态！'% data_t.iloc[0]['asId']
        value = 0
    # 如果冷机组合中有负载率小于65% 的情况，应该进行冷机重组,返回冷机实时功率,据此判断判断优化的组合
    if not (data_t[(data_t['Load_t'] < 60) & (data_t['Load_t'] > 0)].empty):
        # 计算当前组合的实时功率
        total_power_t = data_t[data_t['Load_t'] > 0]['Power_t'].sum()
        Tips = '冷机组合:%s负载率低!应减载。'% data_t.iloc[0]['asId']
        value = total_power_t
    # 只要T_chilled_predict中有1台冷机的拉不下水温,就应该多开冷机了
    if not (data_t[data_t['T_chilled_predict'] > 3].empty):
        # 执行增开机的建议（认为当前组合冷机不满足制冷要求了），返回当前组合的额定功率之和
        # 当前冷机组合的额定功率之和:
        total_power_combins = data_t[data_t['Load_t'] > 0]['Power'].sum()
        Tips = '冷机组合:%s出水温度过高!应加载冷机。'% data_t.iloc[0]['asId']
        value = total_power_combins

    print('冷站当前状态'.center(50, '-'))
    print(Tips)

    return value, data_t


if __name__ == "__main__":

    pass
