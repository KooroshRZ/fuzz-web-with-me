import requests
from time import sleep
import threading
import random
import string
from optparse import OptionParser
import argparse
import json

session = requests.Session()

payloads_list = []
paylosds_size = 0

# config options
input_file = ''
output_file = ''
headers = ''
data = ''
method = ''
url = ''
threads = 0

config_file = 'fuzz-web-with-me\\config.json'

#for debug purpose
proxies = {
    'http' : '127.0.0.1',
    'https' : '127.0.0.1:8080'
}


def distribute_payloads():

    threads_list = []
    global threads
    global method

    for t in range(threads):

        start_offset = t * (paylosds_size//threads)
        end_offset = (t+1) * (paylosds_size//threads)

        thread = threading.Thread(target=send_requests, args=(method, url, start_offset, end_offset, headers, data))

        threads_list.append(thread)
        thread.start()


def send_requests(method, url, start_offset, end_offset, headers=None, data=None):

    if method == 'GET':

        for i in range(start_offset, end_offset):

            payload = payloads_list[i][:-1]

            url = '{}'.format(payload)

            response = session.get(url)

            if response.status_code == 200:
                print("found order with order code : {}".format(payload))

                with open(output_file, 'a') as f1:
                    f1.write(response.text)
                    f1.close()


    elif method == 'POST':

        for i in range(start_offset, end_offset):

            payload = payloads_list[i][:-1]

            data_temp = json.loads(json.dumps(data).replace('FUZZ', payload))
        
            try:
                response = session.post(url, data=data_temp, headers=headers)
            except OSError as err:
                print(err)

            result = json.loads(response.text)

            if result['isRegistered'] == True:
                with open(output_file, 'a') as fo:
                    fo.write("0912" + payload + json.dumps(result) + "\n")
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

    result = json.loads(open(config_file, 'r').read())
    input_file = result['input_file']
    output_file = result['output_file']
    threads = int(result['threads'])
    url = result['url']
    method = result['method']


if __name__ == "__main__":
    
    parse_command()
    initialize()
    distribute_payloads()