import requests
import threading
import random
import string
import argparse
import json
from time import sleep
from sys import stdout

session = requests.Session()
stdout_write = stdout.write

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

# for debug purpose
proxies = {
    'http' : 'http://127.0.0.1:8080',
    'https' : 'https://127.0.0.1:8080'
}


def distribute_payloads():

    threads_list = []
    global threads
    global method

    thread_payload = [[] for x in range(threads)]
    offset = -1

    while offset < paylosds_size:

        for t in range(threads):
            
            thread_payload[t].append(payloads_list[offset][:-1])
            
            offset += 1
            if offset == paylosds_size:
                break

    thread_payload[0].remove(payloads_list[paylosds_size-1][:-1])

    for t in range(threads):
        
        thread = threading.Thread(target=send_requests, args=(thread_payload[t], ))
        threads_list.append(thread)

        try:
            thread.start()
            print("Thread {} started ...".format(t+1))
        except OSError as err:
            print(err)


def send_requests(thread_payload):

    sleep(interval)
    global index
    
    for payload in thread_payload:
        
        index += 1

        stdout_write('\r')
        stdout_write('                                                                                                                     ')
        stdout_write('\r')
        print("[*] sending payload : {}".format(payload), end="\r")

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
                print("    [+] {} : {}".format(index, payload))
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