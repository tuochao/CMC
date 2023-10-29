import json
import pandas as pd
import requests


class ReportProgram:
    message_data_file = 'data/message.csv'
    response_data_file = 'data/response.csv'
    pair_data_file = 'data/pair_data.json'
    interaction_data_file = 'data/interaction.json'

    report_file = 'report/report.txt'

    def __init__(self):
        print('connect service to get latest data')
        try:
            requests.get('http://127.0.0.1:5000/healthCheck')
        except:
            print('service is not running, will get data from file')

        print('----------Report Content:----------')
        self.message_data = pd.read_csv(self.message_data_file, delimiter='|', engine='python')
        self.response_data = pd.read_csv(self.response_data_file, delimiter='|', engine='python')
        with open(self.pair_data_file, 'r', encoding='utf-8') as fp:
            self.pair_data_dict = json.load(fp)
            fp.close()
        with open(self.interaction_data_file, 'r', encoding='utf-8') as fp:
            self.interaction_data = json.load(fp)
            fp.close()

    def generate_report(self):
        total_friend_count = len(self.interaction_data)
        max_message_count = 0
        max_message_key = ''
        max_unique_message_count = 0
        max_unique_message_key = ''
        max_rate_count = 0
        max_rate_key = ''
        for key in self.interaction_data.keys():
            if self.interaction_data[key]['totalMessageCount'] > max_message_count:
                max_message_key = key
                max_message_count = self.interaction_data[key]['totalMessageCount']
            elif self.interaction_data[key]['totalMessageCount'] == max_message_count and max_message_count > 0:
                max_message_key = max_message_key + ',' + key

            if self.interaction_data[key]['uniqueMessageCount'] > max_unique_message_count:
                max_unique_message_key = key
                max_unique_message_count = self.interaction_data[key]['uniqueMessageCount']
            elif self.interaction_data[key]['uniqueMessageCount'] == max_unique_message_count and max_unique_message_count > 0:
                max_unique_message_key = max_unique_message_key + ',' + key

            if self.interaction_data[key]['giveRateCount'] > max_rate_count:
                max_rate_key = key
                max_rate_count = self.interaction_data[key]['giveRateCount']
            elif self.interaction_data[key]['giveRateCount'] == max_rate_count and max_rate_count > 0:
                max_rate_key = max_rate_key + ',' + key

        with open(self.report_file, 'w', encoding='utf-8') as fp:
            print(f'friend count: {total_friend_count}, they are: {list(self.interaction_data.keys())}')
            fp.write(f'friend count: {total_friend_count}, they are: {list(self.interaction_data.keys())}\n')
            print(f'{max_message_key} sent the most messages: {max_message_count}')
            fp.write(f'{max_message_key} sent the most messages: {max_message_count}\n')
            print(f'{max_unique_message_key} sent the most unique messages: {max_unique_message_count}')
            fp.write(f'{max_unique_message_key} sent the most unique messages: {max_unique_message_count}\n')
            print(f'{max_rate_key} gave the most like/unlike: {max_rate_count}')
            fp.write(f'{max_rate_key} gave the most like/unlike: {max_rate_count}\n')
            fp.close()

        with open(self.report_file, 'a', encoding='utf-8') as fp:
            for message_id in self.pair_data_dict.keys():
                message = self.message_data.loc[self.message_data['Id'] == int(message_id), 'Message'].iloc[0]
                like_response_list = []
                unlike_response_list = []
                for friend_name in self.pair_data_dict[message_id].keys():
                    like_response_list.clear()
                    unlike_response_list.clear()
                    if 'like' in self.pair_data_dict[message_id][friend_name] and isinstance(self.pair_data_dict[message_id][friend_name]['like'], int):
                        response = self.response_data.loc[self.response_data['Id'] == int(self.pair_data_dict[message_id][friend_name]['like']), 'Response'].iloc[0]
                        like_response_list.append(response)
                    if 'unlike' in self.pair_data_dict[message_id][friend_name] and isinstance(self.pair_data_dict[message_id][friend_name]['unlike'], list):
                        for unlike_response_id in self.pair_data_dict[message_id][friend_name]['unlike']:
                            response = self.response_data.loc[self.response_data['Id'] == int(unlike_response_id), 'Response'].iloc[0]
                            unlike_response_list.append(response)
                    if len(like_response_list) > 0:
                        print(f'Successful (message: {message}, friend: {friend_name}, response: {like_response_list}) pairs')
                        fp.write(f'Successful (message: {message}, friend: {friend_name}, response: {like_response_list}) pairs\n')
                    if len(unlike_response_list) > 0:
                        print(f'Unsuccessful (message: {message}, friend: {friend_name}, response: {unlike_response_list}) pairs')
                        fp.write(f'Unsuccessful (message: {message}, friend: {friend_name}, response: {unlike_response_list}) pairs\n')
            fp.close()


report_program = ReportProgram()
report_program.generate_report()
