import requests
import threading
import random
import string
import json
from time import sleep
from sys import stdout

session = requests.Session()
stdout_write = stdout.write

payloads_list = []
payloads_size = 0
index = 0
tmp_index = 0

# config options

input_file = ''
output_file = ''

headers = None
post_params = None
post_json = False
method = ''
url = ''

threads = 0
interval = 0
filter_conditions = ''
print_result_on_success = False


config_file = 'config.json'

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
    offset = 0

    while offset < payloads_size:

        for t in range(threads):
            

            rand_index = random.randint(0, payloads_size - offset - 1)
            d = payloads_list[rand_index][:-1]
            payloads_list.pop(rand_index)

            thread_payload[t].append(d)

            offset += 1
            if offset == payloads_size:
                break
            

    #thread_payload[0].remove(payloads_list[payloads_size-1][:-1])

    for t in range(threads):
        
        thread = threading.Thread(target=send_requests, args=(thread_payload[t], ))
        threads_list.append(thread)

        try:
            print("Thread {} started with {} payloads...".format(t+1, len(thread_payload[t])))
            thread.start()
        except OSError as err:
            print(err)


def send_requests(thread_payload):

    global index
    global tmp_index

    sleep(3)
    
    for payload in thread_payload:

        tmp_index += 1
        
        # sleep(interval)

        stdout_write('\r')
        stdout_write('                                                                                                                     ')
        stdout_write('\r')
        
        print("[*] sending payload ({}/{}) : {}".format(tmp_index, payloads_size, payload), end="\r")
        

        if json.dumps(headers).find('FUZZ'):
            temp_headers = json.loads(json.dumps(headers).replace('FUZZ', payload))
        
        if json.dumps(url).find('FUZZ'):
            temp_url = url.replace('FUZZ', payload)    

        if method == 'GET':

            try:
                response = session.get(temp_url, headers=temp_headers)
            except OSError as err:
                print(err)
                continue

        elif method == 'POST':

            if post_json:
                data_temp = json.dumps(json.dumps(post_params).replace('FUZZ', payload))
            else:
                data_temp = json.loads(json.dumps(post_params).replace('FUZZ', payload))

            try:
                response = session.post(temp_url, data=data_temp, headers=temp_headers)
            except OSError as err:
                print(err)
                continue

        
        # write your own extra response processing here
        # result = json.loads(response.text)
        
        code = response.status_code
        content_length = len(response.text)
        result = response.text

        if eval(filter_conditions):

            stdout_write('\r')
            stdout_write('                                                                                                                     ')
            stdout_write('\r')
            

            if print_result_on_success:
                print(response.text)

            index += 1
            with open(output_file, 'a') as fo:
                fo.write("{} : {}\n".format(index, payload))
                print("    [+] {} : {}".format(index, payload))
                fo.close()


def initialize():
    
    global config_file
    
    global input_file
    global output_file
    global threads
    global method
    global url
    global interval
    global filter_conditions
    global print_result_on_success
    global payloads_list
    global payloads_size
    global headers
    global post_params
    global post_json

    config = json.loads(open(config_file, 'r').read())

    input_file = config['input_file']
    output_file = config['output_file']

    payloads_list = open(input_file, 'r').readlines()
    payloads_size = len(payloads_list)


    headers = config['headers']
    post_params = config['post-data']['params']
    post_json = config['post-data']['is-json']
    threads = config['threads']
    url = config['url']
    method = config['method']
    interval = config['interval']
    filter_conditions = config['filter']['conditions']
    print_result_on_success = config['filter']['print-result-on-success']


if __name__ == "__main__":
    
    initialize()
    distribute_payloads()