import requests
from time import sleep
import threading
import random
import string
from optparse import OptionParser
import json

session = requests.Session()
payloads_list = []
paylosds_size = 0


# command line options
input_file = ''
output_file = ''
headers = ''
data = ''
method = ''
url = ''
threads = 3 # default value



'''
proxies = {
    'http' : '127.0.0.1',
    'https' : '127.0.0.1:8080'
}
'''

def distribute_payloads():

    threads_list = []
    global threads

    for t in range(threads):

        start_offset = t * (paylosds_size//threads)
        end_offset = (t+1) * (paylosds_size//threads)

        thread = threading.Thread(target=send_requests, args=(start_offset, end_offset))

        threads_list.append(thread)
        thread.start()


def send_requests(start_offset, end_offset):


    for i in range(start_offset, end_offset):

        payload = payloads_list[i][:-1]

        url = '{}'.format(payload)
        response = session.get(url)

        if response.status_code == 200:
            print("found order with order code : {}".format(payload))

            with open(output_file, 'a') as f1:
                f1.write(response.text)
                f1.close()



def initialize():

    global session

    global payloads_list
    payloads_list = open(input_file, 'r').readlines()

    global paylosds_size
    paylosds_size = len(payloads_list)


def parse_command():
    parser = OptionParser()

    parser.add_option("-i", dest="payloads",  help="read payloads from input file")

    parser.add_option("-o", dest="output", help="write result to output file")

    parser.add_option("-u", dest="url", help="url of target website")

    parser.add_option("-d", dest="data", help="data to send with POST method")

    parser.add_option("-m", dest="method", help="http method")

    parser.add_option("-H", dest="header", help="specific http header")

    parser.add_option("-t", dest="threads", help="number of threads")

    (options, args) = parser.parse_args()
    
    print(options)




if __name__ == "__main__":
    
    parse_command()
    # initialize()
    # distribute_payloads()