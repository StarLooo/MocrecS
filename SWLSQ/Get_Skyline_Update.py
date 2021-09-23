# -*- coding:utf-8 -*-
import math
import random
import time
import numpy as np
import datetime
import pandas as pd
from Circular_Queue import Circular_Queue


class Sliding_Window_Local_k_Skyline_Query:
    # constructor of class Get_Skyline
    def __init__(self, k: int = 2, window_size: int = 1, alpha: float = 0.05, num_samples: int = 100000):
        self.k = k  # k支配关系中的k
        self.window_size = window_size  # the log window size，目前只支持1
        self.num_samples = num_samples
        self.alpha = alpha  # this is the parameter of the forgetting curve
        # ------------------------------------------------------------------------------
        self.updating_infos = {}  # 每日的更新数据
        self.users_courses_events_dict = {}  # 记录所有学生的id的字典
        """
        :param: users_courses_events_dict means: 
            all the points of the user
        :param: users_courses_events_dict[user_id]: 
            the certain user indexed by its user_id
        :param: users_courses_events_dict[user_id][course_id]:
            the certain sc_point represent the learning state for user(user_id) in certain course(course_id)
        :param: users_courses_events_dict[user_id][course_id][event]:
            the count number of a certain event in this sc_point
        """
        # the local candidate in certain combination of courses, the key is bit_map, the val is some user_ids
        self.courses_buckets = {}
        # the graph to show the correlation of buckets, the key is bit_map, the val is some near by buckets' bit_map
        self.bucket_graph = {}
        # the daily updating objects for every user, the key is user_id and the val is his recently accessed object_ids
        self.daily_objects = {}
        self.latest_date = datetime.datetime.strptime("2013-10-27", "%Y-%m-%d")
        # the key of this structure is delta_s, the value is latest update time of this tuple
        self.latest_update_time = {}
        self.latest_position = 0
        self.maxlen_objs = 15
        self.near_dis = 2
        # ------------------------------------------------------------------------------
        self.log_data = self.load_data(self.num_samples)
        # courses records the different courses' course_id
        self.courses = self.log_data["course_id"].unique()
        self.course_events = {'navigate', 'access', 'problem', 'video'}
        self.daily_recommendation = {}
        # ------------------------------------------------------------------------------
        # This part of variables are used for experiment
        self.date_skyline_time = {}
        self.date_recommend_time = {}
        self.date_num_candidate = {}
        self.date_partial_candidate = {}
        self.date_num_bucket = {}
        self.date_log_len = {}
        # 重定向输出
        # self.savestdout = sys.stdout
        # fout = open("k=2,num_samples=1000000.txt", "a+")
        # sys.stdout = fout
        print("Show all courses: ", self.courses)
        print("######################################################################################")

    # load the data from csv
    def load_data(self, num_samples: int):
        log_data = pd.read_csv('../data/reorganized/all_log.csv', nrows=num_samples)

        print("show the first five rows of log_data:")
        print(log_data[0:5])
        print("######################################################################################")

        print("the basic information of log_data:")
        info = log_data.info()
        print("######################################################################################")

        return log_data

    # get updating_infos by log_data
    def get_updating_infos(self):
        self.updating_infos = {}  # reset
        self.latest_date = self.latest_date + datetime.timedelta(days=self.window_size)
        nrow = self.log_data.shape[0]
        while self.latest_position < nrow:
            new_log = self.log_data.iloc[self.latest_position]
            new_date = datetime.datetime.strptime(new_log['time'].split('T')[0], "%Y-%m-%d")
            # the sliding window is full
            if new_date > self.latest_date:
                break
            enrollment_id = new_log['enrollment_id']
            user_id = new_log['user_id']
            course_id = new_log['course_id']
            event = new_log['event']
            object_id = new_log['object_id']
            # updating the daily_objects
            if user_id not in self.daily_objects:
                self.daily_objects[user_id] = Circular_Queue(self.maxlen_objs)
            self.daily_objects[user_id].enQueue(object_id)
            # updating the updating_infos
            if (user_id, course_id) in self.updating_infos:
                if event in self.updating_infos[(user_id, course_id)]:
                    self.updating_infos[(user_id, course_id)][event] += 1
                else:
                    self.updating_infos[(user_id, course_id)][event] = 1
            else:
                self.updating_infos[(user_id, course_id)] = {event: 1}
            self.latest_position += 1

    def run(self, if_test=True):
        while self.latest_position < self.num_samples:
            self.skyline_update()
            if if_test:
                n_candidates = 0
                n_bucket = len(self.courses_buckets.keys())
                self.date_num_bucket[self.latest_date] = n_bucket
                for bit_map in self.courses_buckets:
                    n_candidates += len(self.courses_buckets[bit_map])
                if n_bucket > 0:
                    self.date_num_candidate[self.latest_date] = n_candidates
                    self.date_partial_candidate[self.latest_date] = round(n_candidates / n_bucket, 4)
                else:
                    self.date_num_candidate[self.latest_date] = 0
                    self.date_partial_candidate[self.latest_date] = 0
                recommend_start_time = time.perf_counter_ns()
                choice_list = list(self.users_courses_events_dict.keys())
                # 随机选择100人作推荐，来做测试
                for _ in np.arange(100):
                    lack_cnt = 0
                    recommend_id = random.choice(choice_list)
                    self.daily_recommendation[self.latest_date] = {}
                    recommend_list = self.recommend(recommend_id)
                    if len(recommend_list) < 6:
                        lack_cnt += 1
                    lack_ratio = lack_cnt / 100
                    if lack_cnt > 10:
                        print("lack_cnt of", self.latest_date, ":", lack_cnt)
                    self.daily_recommendation[self.latest_date][recommend_id] = recommend_list
                recommend_end_time = time.perf_counter_ns()
                self.date_recommend_time[self.latest_date] = round((recommend_end_time - recommend_start_time) / 100,
                                                                   2)  # 单位为ns
            else:
                print("------------------------------------------------------------------")
                print("当前日期:", self.latest_date)
                print("当前所有用户的id如下：")
                print(list(self.users_courses_events_dict.keys()))
                loop_flag = True
                while loop_flag:
                    print("请输入想要推荐的用户的id:")
                    user_id = int(input())
                    if user_id in self.users_courses_events_dict.keys():
                        recommend_list = self.recommend(user_id)
                        if len(recommend_list) == 0:
                            print("当前可用于推荐的数据过少，请等待数据量累计至足够用于推荐！")
                        else:
                            print("该用户的今日推荐列表如下：")
                            print(recommend_list)
                        loop_flag = False
                    else:
                        print("输入的用户id不合法，请重新输入！")

    # skyline更新部分
    def skyline_update(self):
        # -----------------------------------skyline更新部分-----------------------------------
        skyline_update_start_time = time.perf_counter()
        old_position = self.latest_position
        # update the infos
        self.get_updating_infos()

        daily_log_len = self.latest_position - old_position
        self.date_log_len[self.latest_date] = daily_log_len
        # print("The latest updating date is: ", self.latest_date)
        # print("The len of updating_infos is: ", len(self.updating_infos))

        # to temporary record new users that learn more than k courses, we call them active_users
        active_users = {}
        # update the users_courses_events_dict
        for user_course_tuple in self.updating_infos:  # user_course_tuple is a two-tuple:(user_id, course_id)
            user_id = user_course_tuple[0]
            course_id = user_course_tuple[1]
            if user_id not in self.users_courses_events_dict:  # decide whether the user is an old user
                updated_user_courses_event_dict = self.create_new_user(
                    user_course_tuple)  # if is not the old user ,then new one
            else:
                updated_user_courses_event_dict = self.update_old_user(
                    user_course_tuple)  # if is an old one, then update it

            # compute the bit_map and positive_num of the new_user
            bit_map, positive_num = self.get_bit_map(updated_user_courses_event_dict)
            if positive_num < self.k:
                # 当positive_num < self.k时该用户不可作为候选人
                continue
            elif positive_num == self.k:
                # if the bucket don't have the bit_map bucket
                if bit_map not in self.courses_buckets:
                    self.courses_buckets[bit_map] = {}  # then add the new bucket
                    self.update_bucket_graph(bit_map, positive_num)  # update the bucket_graph
                is_candidate = True  # is_candidate determine whether the new user can be a new candidate
                for local_candidate_id in list(self.courses_buckets[bit_map]):
                    dominate_relation = self.k_dominate(local_candidate_id, user_id, bit_map)
                    if dominate_relation == 1:  # if the old local_candidate can dominate the new user
                        is_candidate = False
                        break
                    elif dominate_relation == -1:  # if new user can dominate the old local_candidate
                        del self.courses_buckets[bit_map][local_candidate_id]
                if is_candidate:
                    self.courses_buckets[bit_map][user_id] = 1
            else:
                active_users[user_id] = bit_map

        # process the new users in active_users
        for active_user_id in active_users:
            for bit_map in self.courses_buckets:
                active_user_courses_events_dict = self.users_courses_events_dict[active_user_id]
                active_bit_map = active_users[active_user_id]
                if self.bit_map_include(active_bit_map, bit_map):
                    is_candidate = True
                    for local_candidate_id in list(self.courses_buckets[bit_map]):
                        dominate_relation = self.k_dominate(local_candidate_id, active_user_id, bit_map)
                        if dominate_relation == 1:
                            is_candidate = False
                            break
                        elif dominate_relation == -1:
                            del self.courses_buckets[bit_map][local_candidate_id]
                    if is_candidate == 1:
                        self.courses_buckets[bit_map][active_user_id] = 1
        # so far, we have generated local candidates in every courses_buckets[bit_map]

        skyline_update_end_time = time.perf_counter()
        self.date_skyline_time[self.latest_date] = round(1000 * (skyline_update_end_time - skyline_update_start_time),
                                                         2)  # 单位为ms

    def create_new_user(self, user_course_tuple):
        # record the latest update time for the new point
        self.latest_update_time[user_course_tuple] = self.latest_date
        user_id = user_course_tuple[0]
        course_id = user_course_tuple[1]
        # add this new user point to users_courses_events_dict
        self.users_courses_events_dict[user_id] = {course_id: self.updating_infos[user_course_tuple]}
        return self.users_courses_events_dict[user_id]

    def update_old_user(self, user_course_tuple):
        # update the latest update time of the old point
        self.latest_update_time[user_course_tuple] = self.latest_date
        user_id = user_course_tuple[0]
        course_id = user_course_tuple[1]
        time_span = (self.latest_date - self.latest_update_time[(user_id, course_id)]).days
        decrease_rate = self.get_decrease_rate(time_span)
        for event in self.course_events:
            if event in self.updating_infos[user_course_tuple]:
                if course_id in self.users_courses_events_dict[user_id]:
                    if event in self.users_courses_events_dict[user_id][course_id]:
                        self.users_courses_events_dict[user_id][course_id][event] *= decrease_rate
                        self.users_courses_events_dict[user_id][course_id][event] += \
                            self.updating_infos[user_course_tuple][event]
                    else:
                        self.users_courses_events_dict[user_id][course_id][event] = \
                            self.updating_infos[user_course_tuple][event]
                else:
                    self.users_courses_events_dict[user_id][course_id] = {
                        event: self.updating_infos[user_course_tuple][event]}
        return self.users_courses_events_dict[user_id]

    # method to get decline rate
    def get_decrease_rate(self, time_span):
        return math.exp(-self.alpha * time_span)

    # method to get bit_map of point new_student
    def get_bit_map(self, updated_user_courses_event_dict):
        positive_num = 0
        bit_map = ''
        for course_id in self.courses:
            if course_id in updated_user_courses_event_dict:
                bit_map += '1'
                positive_num += 1
            else:
                bit_map += '0'
        return bit_map, positive_num

    def k_dominate(self, user_a_id, user_b_id, bit_map):
        dim_adb, dim_bda = 0, 0
        nevent_adb, nevent_bda = np.zeros(np.size(self.courses)), np.zeros(np.size(self.courses))
        user_a_courses_events_dict = self.users_courses_events_dict[user_a_id]
        user_b_courses_events_dict = self.users_courses_events_dict[user_b_id]

        i = 0
        for bit in bit_map:
            course_id = self.courses[i]
            if bit == '1':
                time_span_a = (self.latest_date - self.latest_update_time[(user_a_id, course_id)]).days
                time_span_b = (self.latest_date - self.latest_update_time[(user_b_id, course_id)]).days
                dcr_a = self.get_decrease_rate(time_span_a)
                dcr_b = self.get_decrease_rate(time_span_b)
                for event in self.course_events:
                    if event in user_a_courses_events_dict[course_id] and \
                            event in user_b_courses_events_dict[course_id]:
                        if user_a_courses_events_dict[course_id][event] * dcr_a > \
                                user_b_courses_events_dict[course_id][event] * dcr_b:
                            nevent_adb[i] += 1
                        elif user_a_courses_events_dict[course_id][event] * dcr_a < \
                                user_b_courses_events_dict[course_id][event] * dcr_b:
                            nevent_bda[i] += 1
                if nevent_adb[i] > nevent_bda[i]:
                    dim_adb += 1
                elif nevent_adb[i] < nevent_bda[i]:
                    dim_bda += 1
                else:
                    return 0

                if dim_adb > 0 and dim_bda > 0:
                    return 0
            i += 1

        if dim_adb == self.k:
            return 1
        elif dim_bda == self.k:
            return -1
        else:
            print("###########WRONG BRANCH IN DOMINATE!##################")
            return 0

    # his function will judge whether the bit_map is included by the more_bit_map
    def bit_map_include(self, active_bit_map, bit_map):
        bit_map_and = ""
        for i in np.arange(np.size(self.courses)):
            if active_bit_map[i] == '1' and bit_map[i] == '1':
                bit_map_and += '1'
            else:
                bit_map_and += '0'
        return bit_map_and == bit_map

    def update_bucket_graph(self, new_bit_map, k_positive):
        if k_positive == self.k:
            # true bucket
            self.bucket_graph[new_bit_map] = {}
        for bit_map in self.courses_buckets:
            both_learn_num = 0
            for i in np.arange(np.size(self.courses)):
                if bit_map[i] == 1 and new_bit_map[i] == 1:
                    both_learn_num += 1
            if both_learn_num >= self.k - self.near_dis:
                self.bucket_graph[new_bit_map] = {}
                # true bucket，双向连接，互为邻居
                if k_positive == self.k:
                    self.bucket_graph[new_bit_map][bit_map] = 1
                    self.bucket_graph[bit_map][new_bit_map] = 1
                # visual bucket，只从虚拟桶单向连接到真实桶
                else:
                    if new_bit_map not in self.bucket_graph:
                        self.bucket_graph[new_bit_map] = {[bit_map]: 1}
                    else:
                        self.bucket_graph[new_bit_map][bit_map] = 1

    def recommend(self, recommend_id):
        recommend_bit_map, positive_num = self.get_bit_map(self.users_courses_events_dict[recommend_id])
        # print("recommend_bit_map is:", recommend_bit_map)
        # print("show the bucket_graph:", self.bucket_graph)
        weight = {}
        w_local = 0
        if positive_num == self.k:
            w_local = 0.5
            # compute weight of objects from local_candidate in local bucket
            num_local_candidate = len(self.courses_buckets[recommend_bit_map])
            # print("num_local_candidate is:", num_local_candidate)
            for local_candidate in self.courses_buckets[recommend_bit_map]:
                for obj in self.daily_objects[local_candidate].queue:
                    if obj not in weight:
                        weight[obj] = w_local / num_local_candidate
                    else:
                        weight[obj] += w_local / num_local_candidate
        else:
            self.update_bucket_graph(recommend_bit_map, positive_num)  # update the bucket_graph

        w_near = 1 - w_local
        if recommend_bit_map in self.bucket_graph:
            num_near_bucket = len(self.bucket_graph[recommend_bit_map])
            # print("num_near_bucket is:", num_near_bucket)
            # compute weight of objects from near_candidate in near bucket
            for bit_map in self.bucket_graph[recommend_bit_map]:
                num_near_candidate = len(self.courses_buckets[bit_map])
                # print("num_near_candidate is:", num_near_candidate)
                for near_candidate in self.courses_buckets[bit_map]:
                    for obj in self.daily_objects[near_candidate].queue:
                        if obj not in weight:
                            weight[obj] = w_near / (num_near_bucket * num_near_candidate)
                        else:
                            weight[obj] += w_near / (num_near_bucket * num_near_candidate)

        recommendation_list = []
        total = 0
        # TODO: use small_root_heap may be faster, but for convenience we use common wat
        for obj in weight:
            if total <= 6:
                recommendation_list.append(obj)
                total += 1
            else:
                min_val = 1000000
                min_pos = -1
                # find min_val in recommendation_list
                for i in np.arange(7):
                    if min_val > weight[obj]:
                        min_val = weight[obj]
                        min_pos = i
                if weight[obj] > min_val:
                    recommendation_list[min_pos] = obj
        return recommendation_list
