import pandas as pd
from itertools import combinations



def all_chillers_combins(df_chillers):

    chiller_counts = len(df_chillers)
    i = 0
    list_combins = []
    list_Power = []
    list_Capacity = []
    list_Run_time = []
    list_COP = []
    while i<chiller_counts:
        i+=1
        list_combins = list_combins+[c for c in combinations(range(chiller_counts),i)]

    for combins in list_combins:
        P_t = 0
        C_t = 0
        T_t = 0
        sum_cop = 0
        for j in combins:
        # 冷机组合的额定功率和
            P_t = P_t + df_chillers['Power'][j]
        # 冷机组合的额定容量和
            C_t = C_t + df_chillers['Capacity'][j]
        # 冷机组合的运行总时间和（非实时参数，而是当月1号的第一条数据）
            T_t = T_t + df_chillers['Run_time'][j]
            sum_cop+= df_chillers['COP'][j] * df_chillers['Capacity'][j]

        avg_cop = sum_cop/C_t
        # 组合的容量加权COP
        avg_cop = round(avg_cop, 3)
        # 得到所有组合的冷机功率、容量、运行时间、加权COP的列表
        list_Power.append(P_t)
        list_Capacity.append(C_t)
        list_Run_time.append(T_t)
        list_COP.append(avg_cop)

    dict_all_chillers_combins = {'list_combins': list_combins, 'list_Power': list_Power, 'list_Capacity': list_Capacity,
                  'list_Run_time': list_Run_time, 'list_COP': list_COP}
    df_data0 = pd.DataFrame(dict_all_chillers_combins)
    df_data0 = df_data0.sort_values(by='list_Power')

    return df_data0


if __name__ == "__main__":

    pass
