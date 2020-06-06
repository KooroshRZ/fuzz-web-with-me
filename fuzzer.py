import requests
import threading
import random
import string
import argparse
import json
from time import sleep

session = requests.Session()

payloads_list = []
paylosds_size = 0

# config options
input_file = ''
output_file = ''
headers = None
data = None
method = ''
url = ''
threads = 0
interval = 0
filter_conditions = ''
print_result_on_success = False
index = 0

config_file = 'fuzz-web-with-me\\config.json'

#for debug purpose
proxies = {
    'http' : 'http://127.0.0.1:8080',
    'https' : 'https://127.0.0.1:8080'
}


def distribute_payloads():

    threads_list = []
    global threads
    global method

    for t in range(threads):

        start_offset = t * (paylosds_size//threads)
        end_offset = (t+1) * (paylosds_size//threads)

        thread = threading.Thread(target=send_requests, args=(start_offset, end_offset))

        threads_list.append(thread)
        thread.start()


def send_requests(start_offset, end_offset):

    sleep(interval)
    global index
    

    for i in range(start_offset, end_offset):

        payload = payloads_list[i][:-1]

        if json.dumps(headers).find('FUZZ'):
            temp_headers = json.loads(json.dumps(headers).replace('FUZZ', payload))
        
        if json.dumps(headers).find('FUZZ'):
            temp_url = url.replace('FUZZ', payload)    

        if method == 'GET':

            try:
                response = session.get(temp_url, headers=temp_headers)
            except OSError as err:
                print(err)
                continue

        elif method == 'POST':

            data_temp = json.loads(json.dumps(data).replace('FUZZ', payload))

            try:
                response = session.post(temp_url, data=data_temp, headers=temp_headers)
            except OSError as err:
                print(err)
                continue

        
        # result = json.loads(response.text)

        code = response.status_code
        content_length = len(response.text)

        if eval(filter_conditions):

            index += 1
            with open(output_file, 'a') as fo:
                fo.write("{} : {}\n".format(index, payload))
                print("{} : {}".format(index, payload))
                fo.close()


def initialize():

    global config_file
    global input_file
    global payloads_list
    global paylosds_size
    global headers
    global data
    
    payloads_list = open(input_file, 'r').readlines()
    paylosds_size = len(payloads_list)

    with open(config_file, 'r') as f:

        config = json.loads(f.read())

        headers = config['headers']
        data = config['data']


def parse_command():
    
    global config_file


    global input_file
    global output_file
    global threads
    global method
    global url
    global interval
    global filter_conditions
    global print_result_on_success

    result = json.loads(open(config_file, 'r').read())
    input_file = result['input_file']
    output_file = result['output_file']
    threads = result['threads']
    url = result['url']
    method = result['method']
    interval = result['interval']
    filter_conditions = result['filter']['conditions']
    print_result_on_success = result['filter']['print-result-on-success']


if __name__ == "__main__":
    
    parse_command()
    initialize()
    distribute_payloads()