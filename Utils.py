import math


# method to get bit_map of point new_student
def get_bit_map(new_student, courses):
    k_positive = 0
    bit_map = ''
    for course_id in courses:
        if course_id in new_student:
            bit_map += '1'
            k_positive += 1
        else:
            bit_map += '0'
    return bit_map, k_positive


# method to get decline rate
def get_dcr(time_span, alpha=0.05):
    return math.exp(-alpha * time_span)


# class Bucket:
#     # this dict records all of the sc_points all buckets
#     # key:enrollment_id, val:sc_point_val
#     all_sc = {}
#     # this dict records the latest update day of all of the sc_points all buckets
#     # key:enrollment_id, val:time
#     latest_updates = {}
#     # this num is used to trim the speed of decline
#     alpha = -0.05
#
#     # constructor of class Box
#     def __init__(self):
#         # this dict records the sc_points which are the local skyline point in this bucket
#         # key:enrollment_id, val:True,mean that the sc_point indexed by enrollment_id is a local candidate
#         self.candidates = {}
#
#     # method to update sc_points by updating_info
#     def update_points(self, enrollment_id, new_point, latest_update):
#         # updating all_sc with and latest_updates info of new_point with its enrollment_id and latest_update
#         Bucket.all_sc[enrollment_id] = new_point
#         timespan = latest_update - Bucket.latest_updates[enrollment_id]
#         Bucket.latest_updates[enrollment_id] = latest_update
#
#         # is_candidate use to record whether the new_sc_point can be a new candidate
#         is_candidate = False
#
#         # judge the relation between old candidates and the new_sc_point
#         for candidate_id in self.candidates.keys():
#             self.candidates[candidate_id] *= get_dcr(timespan, self.alpha)
#             domination = dominate(new_point, self.candidates[candidate_id], latest_update)
#             # means the new_sc_point dominates the old candidate_sc_point
#             if domination == 1:
#                 del self.candidates
#                 is_candidate = True
#             # means the new_sc_point is dominated by the old candidate_sc_point
#             elif domination == -1:
#                 break
#
#         # if the new_sc_point can be a new candidate, then add it to candidates
#         if is_candidate:
#             self.candidates[enrollment_id] = True
