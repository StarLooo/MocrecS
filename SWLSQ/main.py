# -*- coding:utf-8 -*-
import datetime
import os
import pickle
from SWLSQ.Get_Skyline_Update import Sliding_Window_Local_k_Skyline_Query

if __name__ == '__main__':
    # setting paras
    k = 2
    window_size = 1
    alpha = 0.1
    num_samples = 1000000
    latest_pos = 0
    latest_date = datetime.datetime.strptime("2013-10-27", "%Y-%m-%d")

    model = Sliding_Window_Local_k_Skyline_Query(k, window_size, alpha, num_samples)

    model.run(if_test=False)

    os.system("pause")

    # [4944, 12172, 5543, 1627, 10396, 79633, 10883, 26, 8071, 2074, 2282, 9487, 1792, 19954, 15808, 78743, 5660, 1190,
    #  13445, 79763, 6112, 806, 79612, 79816, 34725, 74012, 54550, 1262, 22567, 79874, 45578, 13636, 1231, 79744, 169,
    #  79686, 79779, 79732, 1775, 79815, 2202, 2189, 44021, 5576, 2094]

    actual_days, all_users_id_list, active_users_id_list, now_date = model.update_k_days(k=210, DEBUG=True)
    # for recommend_id in active_users_id_list:
    #     recommend_list = model.recommend(recommend_id=recommend_id)
    #     if len(recommend_list) == 0:
    #         print("当前可用于推荐的数据过少，请等待数据量累计至足够用于推荐！")
    #     else:
    #         print("recommend_id:", recommend_id)
    #         print("该用户的今日推荐列表如下：")
    #         print(recommend_list)
    #     os.system("pause")
    model.run(if_test=False)

    os.system("pause")

    with open("../data/map/date_skyline_time", 'wb') as f:
        pickle.dump(model.date_skyline_time, f)
    with open("../data/map/date_recommend_time", 'wb') as f:
        pickle.dump(model.date_recommend_time, f)
    with open("../data/map/daily_recommendation", 'wb') as f:
        pickle.dump(model.daily_recommendation, f)
    with open("../data/map/date_num_candidate", 'wb') as f:
        pickle.dump(model.date_num_candidate, f)
    with open("../data/map/date_partial_candidate", 'wb') as f:
        pickle.dump(model.date_partial_candidate, f)
    with open("../data/map/date_num_bucket", 'wb') as f:
        pickle.dump(model.date_num_bucket, f)
    with open("../data/map/date_log_len", 'wb') as f:
        pickle.dump(model.date_log_len, f)
    print("######################################################################################")
