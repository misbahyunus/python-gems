#!/usr/bin/env python3

import sys
import json
import datetime
import logging
import requests
import configparser

def main():
    """
    Main funtion to run the code.
    """
    # set up log file
    logging.basicConfig(filename='exchange_rate_info.log', format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
    print ("[{0:%d/%m/%Y %I:%M:%S %p}] Checking config file.".format(datetime.datetime.now()))
    # check existence of config file
    (url, access_key) = read_config()
    if (url == 'None' or access_key == 'None'):
        print ("[{0:%d/%m/%Y %I:%M:%S %p}] Warning : Config file not found or not set up correctly. Please ensure a config file is set up with required connection parameters.".format(datetime.datetime.now()))
        sys.exit(0)
    # HTTPS Header
    headers = {'Content-Type': 'application/json'}
    # log progress
    print ("[{0:%d/%m/%Y %I:%M:%S %p}] Retreiving latest data.".format(datetime.datetime.now()))
    # get the latest exchange rates from fixer.io in JSON format
    rate_info = get_response(get_url(url, access_key), headers)

    if rate_info is not None:
        if (not rate_info['success']):
            print ("[{0:%d/%m/%Y %I:%M:%S %p}] Error : {1}".format(datetime.datetime.now(), rate_info['error']['info']))
            #print (rate_info['error']['info'])
        else:
            # log progress
            print ("[{0:%d/%m/%Y %I:%M:%S %p}] Displaying Currency Rates.".format(datetime.datetime.now()))
            display_rates(rate_info)
    else:
        print('[!] Request Failed')

def get_url(api_url_base, api_access_key):
    """
    Gets the full Web API url.
    """
    # Fixer.io format
    api_format = '1'
    # Fixer.io base currency
    api_base_currency = 'AUD'

    return (api_url_base.format(api_access_key, api_format))

def get_response(address, header):
    """
    Gets the JSON data from the Web API.
    """    
    # REST Web API URL
    api_url = address
    # JSON response
    response = requests.get(api_url, headers=header)
    # HTTP response check
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None

def read_config():
    """
    Reads the data source settings from the config file.
    """
    config = configparser.ConfigParser()
    try:
        config.read('config.ini')
    except Exception as e:
        logging.error(e)
        print ("No config file found!")
        sys.exit(0)
    else:
        base_url = config.get('DEFAULT', 'url', fallback='None')
        access_key = config.get('DEFAULT', 'key', fallback='None')

    return (base_url, access_key)

def display_rates(exchange_rates):
    """
    Displays the currency rates.    
    """
    base_AUD_rate = 1

    for k,v in exchange_rates['rates'].items():
        if k == 'AUD':
            base_AUD_rate = v

    for k,v in exchange_rates['rates'].items():
        currency_code = k
        currency_rate = round(v / base_AUD_rate, 2)
        print ('[{0:%d/%m/%Y %I:%M:%S %p}] 1 AUD = {1} {2}'.format(datetime.datetime.now(), currency_rate, currency_code))   

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()