import datetime
from Loader import load_data, get_updating_infos
from Utils import get_bit_map, get_dcr
import numpy as np
import sys


class Get_Skyline:
    # constructor of class Get_Skyline
    def __init__(self, k=2, window_size=1, alpha=0.05, num_samples=100000):
        self.k = k  # determine the k of k-domination
        self.updating_infos = {}  # the dict of the changing data of students
        self.all_students = {}  # the dict of the all students, key is the student's user_id
        """
        :param: all_students means: 
            all the points of the student
        :param: all_students[user_id]: 
            the certain student indexed by its user_id
        :param: all_students[user_id][course_id]:
            the certain sc_point represent the learning state for student(user_id) in certain course(course_id)
        :param: all_students[user_id][course_id][event]:
            the count number of a certain event in this sc_point
        """
        # the local candidate in certain combination of courses, the key is bit_map, the val list of user_id
        self.courses_bucket = {}
        self.window_size = window_size  # the log window size
        self.latest_date = datetime.datetime.strptime("2013-10-27", "%Y-%m-%d")
        self.num_samples = num_samples
        self.latest_update = {}  # the key of this structure is delta_s, the value is latest update time of this tuple
        self.alpha = alpha  # this is the parameter of the forgetting curve
        self.log_data = load_data(self.num_samples)
        self.courses = self.log_data["course_id"].unique()  # courses records the different courses' course_id
        self.latest_pos = 0
        self.course_events = {'navigate', 'access', 'problem', 'video'}  # Todo: will add all the key in the courses
        self.savestdout = sys.stdout
        fout = open("k=3,num_samples=1000000.txt", "a+")
        sys.stdout = fout
        print("courses = ", self.courses)

    def run(self):

        # update the infos
        self.updating_infos, self.latest_pos, self.latest_date = get_updating_infos(self.log_data, self.window_size,
                                                                                    self.latest_pos, self.latest_date)
        print("The latest updating date is: ", self.latest_date)
        print("The len of updating_infos is: ", len(self.updating_infos))
        # to temporary record new students that learn more than k courses
        more_courses_students = {}

        # print(self.updating_infos)
        # print(self.updating_infos.keys())

        # update the all_students
        for delta_sc in self.updating_infos:  # delta_s is a two-tuple:(user_id, course_id)
            new_student_id = delta_sc[0]  # new_student_id is the user_id of the student like 23551
            if new_student_id not in self.all_students:  # decide whether the student is an old point
                new_student = self.create_new_student(delta_sc)  # if is not the old point ,then new one
            else:  # Todo: maybe the structure above and below can be simplified
                new_student = self.update_old_student(delta_sc)  # if is an old one, then update it

            # compute the bit_map of the new_student
            bit_map, k_positive = get_bit_map(new_student, self.courses)
            if k_positive < self.k:
                # Todo: this brunch isn't be created well
                continue
            elif k_positive == self.k:
                if bit_map not in self.courses_bucket:  # if the bucket don't have the bit_map bucket, then new one
                    self.courses_bucket[bit_map] = {}
                is_candidate = True  # is_candidate determine whether the new student can be a new candidate
                for local_candidate_id in list(self.courses_bucket[bit_map]):
                    # Todo: the latest time didn't add
                    dominate_relation = self.dominate(local_candidate_id, new_student_id, bit_map)
                    if dominate_relation == 1:  # if the old local_candidate can dominate the new student
                        is_candidate = False
                        break
                    elif dominate_relation == -1:  # if new student can dominate the old local_candidate
                        del self.courses_bucket[bit_map][local_candidate_id]
                if is_candidate:
                    self.courses_bucket[bit_map][new_student_id] = 1

            else:
                more_courses_students = {new_student_id: bit_map}

        # process the new students in more_courses_student
        for student_id in more_courses_students:
            for bit_map in self.courses_bucket:
                student = self.all_students[student_id]
                more_bit_map = more_courses_students[student_id]
                if self.bit_map_include(more_bit_map, bit_map):
                    is_candidate = True
                    for local_candidate_id in list(self.courses_bucket[bit_map]):
                        dominate_relation = self.dominate(local_candidate_id, student_id, bit_map)
                        if dominate_relation == 1:  # should add the bit_map in dominate
                            is_candidate = False
                            break
                        elif dominate_relation == -1:
                            del self.courses_bucket[bit_map][local_candidate_id]
                    if is_candidate == 1:
                        self.courses_bucket[bit_map][student_id] = 1
        # Todo: so far, we have local candidates in every courses_bucket[bit_map]

        n_candidates = 0
        print("The num of buckets: ", len(self.courses_bucket.keys()))
        print(self.courses_bucket)
        for bit_map in self.courses_bucket:
            n_candidates += len(self.courses_bucket[bit_map])
        print("The num of local candidates: ", n_candidates)
        if len(self.all_students) > 0:
            print("The partial of local candidates: ", n_candidates / len(self.all_students))

    def create_new_student(self, delta_sc):
        # Todo: this function will add the student corresponding the delta's to the all_students
        # Todo: and return the new student point
        # record the latest update time for the new point
        self.latest_update[delta_sc] = self.latest_date
        student_id = delta_sc[0]
        course_id = delta_sc[1]
        # for key in self.delta_students[delta_s].keys():
        #     self.all_students[student_id][course_id][key] = self.delta_students[delta_s][key]
        # add this new student point to all_students
        self.all_students[student_id] = {course_id: self.updating_infos[delta_sc]}
        return self.all_students[student_id]

    def update_old_student(self, delta_sc):
        # Todo: this function will update one student according to the delta's,
        # Todo: and be care about deleting the previous point of the student and adding the new one's
        # Todo: and return the new student point
        # update the latest update time of the old point
        self.latest_update[delta_sc] = self.latest_date
        student_id = delta_sc[0]
        course_id = delta_sc[1]
        time_span = (self.latest_date - self.latest_update[(student_id, course_id)]).days
        dcr = get_dcr(time_span, self.alpha)
        for event in self.course_events:
            if event in self.updating_infos[delta_sc]:
                if course_id in self.all_students[student_id]:
                    if event in self.all_students[student_id][course_id]:
                        self.all_students[student_id][course_id][event] *= dcr
                        self.all_students[student_id][course_id][event] += \
                            self.updating_infos[delta_sc][event]
                    else:
                        self.all_students[student_id][course_id][event] = \
                            self.updating_infos[delta_sc][event]
                else:
                    self.all_students[student_id][course_id] = {event: self.updating_infos[delta_sc][event]}
        return self.all_students[student_id]

    def dominate(self, student_a_id, student_b_id, bit_map):
        dim_adb, dim_bda = 0, 0
        nevent_adb, nevent_bda = np.zeros(np.size(self.courses)), np.zeros(np.size(self.courses))
        student_a = self.all_students[student_a_id]
        student_b = self.all_students[student_b_id]

        i = 0
        for bit in bit_map:
            course_id = self.courses[i]
            if bit == '1':
                time_span_a = (self.latest_date - self.latest_update[(student_a_id, course_id)]).days
                time_span_b = (self.latest_date - self.latest_update[(student_b_id, course_id)]).days
                dcr_a = get_dcr(time_span_a, self.alpha)
                dcr_b = get_dcr(time_span_b, self.alpha)
                for event in self.course_events:
                    if event in student_a[course_id] and event in student_b[course_id]:
                        if student_a[course_id][event] * dcr_a > student_b[course_id][event] * dcr_b:
                            nevent_adb[i] += 1
                        elif student_a[course_id][event] * dcr_a < student_b[course_id][event] * dcr_b:
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

    def bit_map_include(self, more_bit_map, bit_map):
        # Todo: this function will judge whether the bit_map is included by the more_bit_map
        bit_map_and = ""
        for i in np.arange(np.size(self.courses)):
            if more_bit_map[i] == '1' and bit_map[i] == '1':
                bit_map_and += '1'
            else:
                bit_map_and += '0'
        return bit_map_and == bit_map
