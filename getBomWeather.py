#!/usr/bin/env python3
# getBomWeather.py - Fetches the latest weather update from BOM website based on supplied state and suburb.

import requests
import bs4
import webbrowser
import sys
import datetime

def main():
    """
    Main funtion to run the code.
    """
    states = ['vic', 'nsw', 'wa', 'sa', 'nt', 'tas']
    # if no arguments are given, print a helpful message.
    if len (sys.argv) == 1:
        #print ('Enter State code (choose from VIC, NSW, WA, SA, NT, TAS')
        stateInput = input('Enter State code (choose from VIC, NSW, WA, SA, NT, TAS): ')        
        if stateInput.lower() not in states:
            print ('WARNING : Invalid choice!')
            sys.exit(0)
        # get suburb name from user
        cityInput = input('Enter Suburb name (replace any spaces with a hyphen) : ')
    elif len(sys.argv) == 3:
        stateInput = sys.argv[1]
        cityInput = sys.argv[2]
    else:
        print ("[{0:%d/%m/%Y %I:%M:%S %p}] Usage: {1} <state> <suburb>".format(datetime.datetime.now(), sys.argv[0]))
        sys.exit(0)
    # display text while downloading the weather page
    print('Fetching weather... ')
    # format URL for BOM weather data
    url = 'http://m.bom.gov.au/{0}/{1}/' .format(stateInput, cityInput)
    #print (url)
    try:
        # fetch the web page
        res = requests.get(url)
        # raise if any error
        res.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print ('WARNING : Invalid location name. Please try again.')
        print ("Usage: {0} <state (short code)> <suburb>".format(sys.argv[0]))
        sys.exit(0)
        
    soup = bs4.BeautifulSoup(res.text, "lxml")
    # select element with class 'location-name'
    locationName = soup.select('.location-name')
    print ('Location : {0}'.format(locationName[0].getText().strip()))
    # select elemet with class 'current-temp'
    currentTemp = soup.select('.current-temp')
    print ('Current temp : {0}C'.format(currentTemp[0].getText().strip()))
    # select element with class 'feels-like' and the element <p> within it
    feelsLike = soup.select('.feels-like p')
    print ('Feels like : {0}'.format(feelsLike[0].getText()))
    # select element with class 'current-time'
    observedTime = soup.select('.current-time')
    print ('[Observed at : {0}]'.format(' '.join(observedTime[0].getText().split())))
    
# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()