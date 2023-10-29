import argparse
import json

import requests

# alias talk-to-george='python3 test_driver.py'
parser = argparse.ArgumentParser(description='input friend name')
parser.add_argument('--friend', '-f', help="input friend name", required=True)
args = parser.parse_args()
friend_name = args.friend

try:
    requests.get('http://127.0.0.1:5000/healthCheck')
except:
    raise ConnectionRefusedError('can not connect to CMC service!')

print(f'Hello {friend_name}!')

while True:
    message = input(f'{friend_name}: ')
    # Bonus2, flesh data event
    if message == 'fleshdata':
        response = requests.post(url='http://127.0.0.1:5000/saveData')
        print(response.text)
    # Bonus3, inspect internal in memory data structures
    elif message == 'inspect':
        parameter_dict = {'1': 'message', '2': 'response', '3': 'pairs', '4': 'interaction'}
        print('[inspect options]: 1 - message, 2 - response, 3 - pairs, 4 - interaction data, 5 - cancel')
        key = input(f'[option]: ')
        if key in parameter_dict.keys():
            params = {'type': parameter_dict[key]}
            response = requests.get(url='http://127.0.0.1:5000/inspect', params=params)
            print(response.text)
    else:
        send_message_data = {
            'friendName': friend_name,
            'message': message
        }
        response = requests.post(url='http://127.0.0.1:5000/message', headers={'content-type': 'application/json'}, data=json.dumps(send_message_data))
        print(f'CMC: {response.text}')
        print('[CMC Survey]: 1 - like, 2 - unlike, 3 - continue')
        rate = input(f'[{friend_name}]: ')
        while rate not in ['1', '2', '3']:
            print('[CMC Survey]: please choose a valid option!')
            rate = input(f'[{friend_name}]: ')
        if rate == '1':
            is_like = True
        elif rate == '2':
            is_like = False
        else:
            is_like = None
        # only receive valid rate feedback
        if is_like is not None:
            send_rate_data = {
                "friendName": friend_name,
                "like": is_like
            }
            requests.post(url='http://127.0.0.1:5000/rate', headers={'content-type': 'application/json'}, data=json.dumps(send_rate_data))
