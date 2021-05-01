import datetime
import pandas as pd
from Circular_Queue import Circular_Queue


# load the data from csv
# TODO: to check whether the data format is appropriate
def load_data(num_samples):
    # read the csv from all_log.csv
    log_data = pd.read_csv('data/reorganized/all_log.csv', nrows=num_samples)

    print("show the first five rows of log_data:")
    print(log_data[0:5])
    print("######################################################################################")

    print("the information of log_data:")
    info = log_data.info()
    print("######################################################################################")

    return log_data


# get updating_infos by log_data
def get_updating_infos(daily_objects, log_data, window_size, latest_pos, latest_date, maxlen_objs=15):
    updating_infos = {}
    latest_date = latest_date + datetime.timedelta(days=window_size)
    nrow = log_data.shape[0]
    while latest_pos < nrow:
        new_log = log_data.iloc[latest_pos]
        new_date = datetime.datetime.strptime(new_log['time'].split('T')[0], "%Y-%m-%d")
        # the sliding window is full
        if new_date > latest_date:
            break
        enrollment_id = new_log['enrollment_id']
        user_id = new_log['user_id']
        course_id = new_log['course_id']
        event = new_log['event']
        object_id = new_log['object_id']
        # updating the daily_objects
        if user_id not in daily_objects:
            daily_objects[user_id] = Circular_Queue(maxlen_objs)
        daily_objects[user_id].enQueue(object_id)
        # updating the updating_infos
        if (user_id, course_id) in updating_infos:
            if event in updating_infos[(user_id, course_id)]:
                updating_infos[(user_id, course_id)][event] += 1
            else:
                updating_infos[(user_id, course_id)][event] = 1
        else:
            updating_infos[(user_id, course_id)] = {event: 1}
        latest_pos += 1

    return updating_infos, latest_pos, latest_date
