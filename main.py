import datetime
from Get_Skyline_Update import Get_Skyline

# def _init(parser):
#     parser.add_argument('--algorithm', action='store')
#     parser.add_argument('--window_size', type=int, action='store')
#     parser.add_argument('--missing_rate', type=float, action='store')
#     parser.add_argument('--num_samples', type=int, action='store')
#     parser.add_argument('--num_attrs', type=int, action='store')
#     parser.add_argument('--print_step', type=int, action='store')


if __name__ == '__main__':
    # setting paras
    k = 3
    window_size = 1
    alpha = 0.05
    num_samples = 1000000
    latest_pos = 0
    latest_date = datetime.datetime.strptime("2013-10-27", "%Y-%m-%d")
    # log_data = load_data(num_samples)
    # print(log_data.shape)
    # print(log_data.iloc[0])
    # print(log_data.iloc[4])
    # updating_infos, latest_pos, latest_date = get_updating_infos(log_data, 1, latest_pos, latest_date)

    model = Get_Skyline(k, window_size, alpha, num_samples)
    while model.latest_pos < num_samples:
        model.run()
        print("######################################################################################")

    # # test
    # testlist = {}
    # s = {}
    # for key in updating_infos[(23551, 36)].keys():
    #     s[key] = updating_infos[(23551, 36)][key]
    #     print(s)
    # print("######################################################################################")
    # print('problem' in s)

    # model = KISkyline(num_samples)
    # run model
    # model.run()
