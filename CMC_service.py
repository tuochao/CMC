import json
from collections import namedtuple
import pandas as pd
import random
from log import logger


class CMCService:
    message_data_file = 'data/message.csv'
    response_data_file = 'data/response.csv'
    pair_data_file = 'data/pair_data.json'
    interaction_data_file = 'data/interaction.json'
    __instance = None

    def __init__(self):
        self.message_data = pd.read_csv(self.message_data_file, delimiter='|', engine='python')
        self.response_data = pd.read_csv(self.response_data_file, delimiter='|', engine='python')
        with open(self.pair_data_file, 'r', encoding='utf-8') as fp:
            self.pair_data_dict = json.load(fp)
            fp.close()
        with open(self.interaction_data_file, 'r', encoding='utf-8') as fp:
            self.interaction_data = json.load(fp)
            fp.close()
        self.last_record = {}

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
            return cls.__instance

    def find_message(self, message_content: str):
        # find message id
        is_new_message = False
        matched_message_data = self.message_data.loc[self.message_data['Message'] == message_content]
        if matched_message_data.empty:
            # new message, add into message data list
            is_new_message = True
            largest_id = self.message_data.iloc[-1][0]
            message_id = largest_id + 1
            new_message = {'Id': message_id, 'Message': message_content}
            self.message_data.loc[len(self.message_data)] = new_message
            message_content = new_message['Message']
        else:
            message_id = matched_message_data['Id'].iloc[0]
            message_content = matched_message_data['Message'].iloc[0]
            print(f'message id: {message_id}')
        MatchedMessage = namedtuple('MatchedMessage', ('message_id', 'message_content', 'is_new_message'))
        matched_message = MatchedMessage(message_id, message_content, is_new_message)
        return matched_message

    def select_response(self, friend_name: str, message_content: str):
        matched_message = self.find_message(message_content)
        message_id = matched_message.message_id
        self.last_record.setdefault(friend_name, {})
        self.last_record[friend_name]['message_id'] = message_id

        # convert to str for using in JSON key
        message_id = str(message_id)
        self.pair_data_dict.setdefault(message_id, {})
        # new friend
        if friend_name not in self.interaction_data.keys():
            self.interaction_data[friend_name] = {
                "id": "",
                "totalMessageCount": 0,
                "uniqueMessageCount": 0,
                "giveRateCount": 0
            }
        self.interaction_data[friend_name]['totalMessageCount'] += 1
        new_friend_pair_data = {
            'like': None,
            "unlike": [],
        }
        self.pair_data_dict[message_id].setdefault(friend_name, new_friend_pair_data)

        # new message
        if matched_message.is_new_message:
            self.interaction_data[friend_name]['uniqueMessageCount'] += 1

        all_response_id_list = self.response_data.loc[:, "Id"].tolist()
        # if there is already paired response
        if message_id in self.pair_data_dict.keys():
            paired_data = self.pair_data_dict.get(message_id)
            # this friend already has like answer
            if friend_name in paired_data.keys() and isinstance(paired_data[friend_name].get('like', None), int):
                like_response_id = paired_data[friend_name]['like']
            else:
                my_unlike_response_id_list = paired_data[friend_name]['unlike']
                # check if other friends have like answer
                like_response_id_list = [paired_data[key]['like'] for key in paired_data.keys() if isinstance(paired_data[key].get('like', None), int)]
                like_response_id_list = list(filter(lambda x: x not in my_unlike_response_id_list, like_response_id_list))
                # other friends have like answer
                if len(like_response_id_list) > 0:
                    like_response_id = like_response_id_list[random.randint(0, len(like_response_id_list) - 1)]
                else:
                    # no like answer, random select a response and exclude all unlike id
                    # handle the case all response this one unlike
                    if len(my_unlike_response_id_list) == len(all_response_id_list):
                        return 'There is no appropriate response! Seems you do not like all of my response :('
                    temp = list(filter(lambda x: x not in my_unlike_response_id_list, all_response_id_list))

                    # handle the case all response other friends unlike
                    others_unlike_response_id_list = [paired_data[key]['unlike'] for key in paired_data.keys()
                                                      if key != friend_name and isinstance(paired_data[key].get('unlike', None), list)]
                    others_unlike_response_id_list = list(flatten(others_unlike_response_id_list))
                    temp = list(filter(lambda x: x not in others_unlike_response_id_list, temp))
                    # if all response other friends unlike, will still random choose a response from others unlike response
                    if len(temp) == 0:
                        others_unlike_response_id_list = list(filter(lambda x: x not in my_unlike_response_id_list, others_unlike_response_id_list))
                        like_response_id = others_unlike_response_id_list[random.randint(0, len(others_unlike_response_id_list) - 1)]
                    else:
                        # else random choose a response exclude all unlike id
                        like_response_id = temp[random.randint(0, len(temp) - 1)]
        else:
            # no pair data, new message, return random response
            like_response_id = all_response_id_list[random.randint(0, len(all_response_id_list) - 1)]

        self.last_record[friend_name]['response_id'] = like_response_id

        # find response according to response id and return
        matched_response = self.response_data.loc[self.response_data['Id'] == int(like_response_id), 'Response'].iloc[0]
        print(matched_response)
        logger.info(f'friend {friend_name} send message: {message_content}, CMC response: {matched_response}')
        return matched_response

    def rate_func(self, friend_name: str, message_content, response_content, is_like: bool):
        # rate the last message and response
        RateResult = namedtuple('RateResult', ('is_success', 'message'))
        if message_content is None or response_content is None:
            if friend_name not in self.last_record.keys():
                return False, 'please send message firstly before give rate'

            message_id = self.last_record[friend_name].get('message_id', None)
            response_id = self.last_record[friend_name].get('response_id', None)
            if message_id is None or response_id is None:
                return False, 'please send message firstly before give rate'
            message_content = self.message_data.loc[self.message_data['Id'] == message_id, 'Message'].iloc[0]
            response_content = self.response_data.loc[self.response_data['Id'] == response_id, 'Response'].iloc[0]

            # convert to str for using in JSON key
            message_id = str(message_id)
        else:
            # rate the message and response in body directly
            matched_message = self.find_message(message_content)
            message_id = str(matched_message.message_id)

            matched_response = self.response_data.loc[self.response_data['Response'] == response_content]
            if matched_response.empty:
                logger.error(f'send response:{response_content} does not exist!')
                rate_result = RateResult(False, f'send response:{response_content} does not exist!')
                return rate_result
            else:
                response_id = int(matched_response['Id'].iloc[0])
        self.pair_data_dict.setdefault(message_id, {})

        # new friend
        if friend_name not in self.interaction_data.keys():
            self.interaction_data[friend_name] = {
                "id": "",
                "totalMessageCount": 0,
                "uniqueMessageCount": 0,
                "giveRateCount": 0
            }
        self.interaction_data[friend_name]['giveRateCount'] += 1

        new_friend_pair_data = {
            'like': None,
            "unlike": [],
        }
        self.pair_data_dict[message_id].setdefault(friend_name, new_friend_pair_data)

        # check unlike field type, handle empty value
        if 'unlike' not in self.pair_data_dict[message_id][friend_name].keys():
            self.pair_data_dict[message_id][friend_name]['unlike'] = []

        if is_like:
            self.pair_data_dict[message_id][friend_name]['like'] = response_id
            if response_id in self.pair_data_dict[message_id][friend_name]['unlike']:
                self.pair_data_dict[message_id][friend_name]['unlike'].remove(response_id)
            logger.info(f'friend {friend_name} like response: {response_content} of message: {message_content}')
        else:
            self.pair_data_dict[message_id][friend_name]['unlike'].append(response_id)
            # remove duplicate id
            self.pair_data_dict[message_id][friend_name]['unlike'] = list(set(self.pair_data_dict[message_id][friend_name]['unlike']))
            if response_id == self.pair_data_dict[message_id][friend_name]['like']:
                self.pair_data_dict[message_id][friend_name]['like'] = None
            logger.info(f'friend {friend_name} does NOT like response: {response_content} of message: {message_content}')
        rate_result = RateResult(True, 'successfully give rate')
        return rate_result

    # serialize self.message_data, self.pair_data_dict and self.interaction_data
    def save_data(self):
        self.message_data.to_csv(self.message_data_file, sep='|', index=None)
        with open(self.pair_data_file, 'w', encoding='utf-8') as fp:
            json.dump(self.pair_data_dict, fp)
            fp.close()
        with open(self.interaction_data_file, 'w', encoding='utf-8') as fp:
            json.dump(self.interaction_data, fp)
            fp.close()

    # allow user to inspect internal memory data
    def inspect(self, parameter):
        if parameter == 'message':
            return self.message_data.to_string(index=False)
        elif parameter == 'response':
            return self.response_data.to_string(index=False)
        elif parameter == 'pairs':
            return self.pair_data_dict
        elif parameter == 'interaction':
            return self.interaction_data
        else:
            return ''


def flatten(item_list, ignore_types=(str, int)):
    for item in item_list:
        if isinstance(item, list) and not isinstance(item, ignore_types):
            yield from flatten(item)
        else:
            yield item


cmc_service = CMCService()

