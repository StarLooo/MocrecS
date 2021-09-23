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
    num_samples = 100000
    latest_pos = 0
    latest_date = datetime.datetime.strptime("2013-10-27", "%Y-%m-%d")

    model = Sliding_Window_Local_k_Skyline_Query(k, window_size, alpha, num_samples)

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
