# 以下函数根据预测的冷机组合实时参数（当前组合），预测到的未来3H最大负荷，预测模式。得到此时冷机的合理组合
import pandas as pd
from all_chillers_combins import all_chillers_combins


# 函数修改了当前冷机组合的df_data，增加了开关机的建议
def chiller_combins_suggestion(df_data, max_load_in3H, mode='P'):

    if mode=='P':
        Q_or_P = 'list_Power'
    elif mode=='Q':
        Q_or_P = 'list_Capacity'

    #now_combins = df_data[['Chiller_ID', 'Load_t']]
    #now_combins['state'] = now_combins['Load_t'] > 0
    #now_combins.drop('Load_t')
    all_combins = all_chillers_combins(df_data)

    if all_combins[Q_or_P].max()<max_load_in3H: #预测结果大于总装机总量的情况
        df_data['suggestion_state'] = True
    else:
        all_combins = all_combins.loc[all_combins[Q_or_P] > 1.1 * max_load_in3H]  #筛选出满足最大负荷的组合（乘1.1，由于现场一般有电流负载率85%的限制）

        msk1 = all_combins.iloc[0][Q_or_P]  # 筛选满足最大负荷的组合，最接近的
        all_combins = all_combins.loc[all_combins[Q_or_P] == msk1]  # 选择容量最接近预测3H最大负荷的冷机组合
        all_combins = all_combins.sort_values(['list_COP'], ascending=False)  # 组合按照COP最高排序
        msk2 =all_combins.iloc[0]['list_COP']
        #print(msk2)
        all_combins = all_combins.loc[all_combins['list_COP'] > msk2*0.95]  # 选择大于最高COP*0.95的组合，认为都可以（可能有若干个组合）
        #print(all_combins)
        all_combins = all_combins.sort_values(['list_Run_time'], ascending=True)  # 按照运行时间升序
        #print(all_combins)
        all_combins = all_combins.iloc[:1]  # 直接选择运行时间最短的组合
        sug_combins = all_combins.iloc[0]['list_combins']
        list_a = [False, ] * len(df_data)
        for i in sug_combins:
            list_a[i] = True
        df_data['suggestion_state'] = list_a

    return df_data


if __name__ == "__main__":

    pass
