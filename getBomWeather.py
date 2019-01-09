#!/usr/bin/env python3
# getBomWeather.py - Fetches the latest weather update from BOM website based on supplied state and city as arguments
#                    OR by city name OR by postcode.

import requests
import bs4
import sys
import datetime
import json

def main():
    """
    Main function to run the code.
    """
    # define Australian states
    states = ['vic', 'nsw', 'wa', 'sa', 'nt', 'tas']
    # if no arguments are given, print a helpful message.
    if len (sys.argv) == 1:
        # get suburb name from user
        cityInput = input('Enter City name (replace any spaces with a hyphen) or postcode: ')
        if cityInput.isnumeric():
            processPostcode(cityInput)
        else:
            #print ('Enter State code (choose from VIC, NSW, WA, SA, NT, TAS')
            stateInput = input('Enter State code (choose from VIC, NSW, WA, SA, NT, TAS): ')        
            if stateInput.lower() not in states:
                print ('WARNING : Invalid choice!')
                sys.exit(0)
            print('Fetching weather... ')
            # fetch BOM weather data
            result = fetchBomWeather(stateInput, cityInput)
            if result is not None:
                displayWeather(result)       
    elif len(sys.argv) == 3:
        stateInput = sys.argv[1]
        cityInput = sys.argv[2]
        # validation
        if stateInput.lower() not in states:
            print ('Invalid State code supplied. Please choose from (VIC, NSW, WA, SA, NT, TAS).')
            sys.exit(0)
        # fetch BOM weather data
        result = fetchBomWeather(stateInput, cityInput)
        if result is not None:
            displayWeather(result)
    else:
        print ("[{0:%d/%m/%Y %I:%M:%S %p}] Usage: {1} <state> <city>".format(datetime.datetime.now(), sys.argv[0]))
        sys.exit(0)    

def processPostcode(cityInput):
    """
    Processes the postcode supplied by the user.
    """
    cityName = ''
    stateCode = ''
    postCode = int(cityInput)
    # get info for the postcode
    cityInfo = fetchCityInfo(postCode)

    if cityInfo != []:
        # get results length
        if len(cityInfo) == 1:
            # 
            cityName = cityInfo[0]['name'].lower().replace(' ', '-')
            stateCode = cityInfo[0]['state']['abbreviation'].lower()
            print('Fetching weather... ')
            # fetch BOM weather data
            result = fetchBomWeather(stateCode, cityName)
            if result is not None:
                displayWeather(result)
        else:
            print("Multiple locations found!")
            count = 1
            for n in cityInfo:
                # display location suggestions
                print("{0}. {1}".format(count, n['name']))
                count = count + 1

            while 1:
                # get user selection of location
                userChoice = input('Select a number from above (0 to quit) : ')
                # check for valid integer
                if userChoice.isnumeric():
                    if int(userChoice) == 0:
                        break
                    if int(userChoice) <= len(cityInfo):
                        cityName = cityInfo[int(userChoice) - 1]['name'].lower().replace(' ', '-')
                        stateCode = cityInfo[int(userChoice) - 1]['state']['abbreviation'].lower()
                        # fetch BOM weather data
                        result = fetchBomWeather(stateCode, cityName)
                        if result is not None:
                            displayWeather(result)
                        break
    else:
        print("Invalid postcode!")

def fetchCityInfo(postCode):
    """
    Returns the JSON data from the postcode API after supplying postcode.
    """
    # HTTPS Header
    header = {'Content-Type': 'application/json'}
    # API URL to fetch info
    api_url = 'http://v0.postcodeapi.com.au/suburbs/{0}.json'.format(postCode)
    
    # JSON response
    response = requests.get(api_url, headers=header)
    # HTTP response check
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None

def fetchBomWeather(stateInput, cityInput):
    """
    Fetches the BOM weather for the supplied state / city.
    """
    # format URL for BOM weather data
    url = 'http://m.bom.gov.au/{0}/{1}/' .format(stateInput, cityInput)
    #print (url)
    try:
        # fetch the web page
        res = requests.get(url)
        # raise if any error
        res.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print ('WARNING : Invalid City name. Please try again.')
        #print ("Usage: {0} <state (short code)> <suburb>".format(sys.argv[0]))
        sys.exit(0)
    
    return res

def displayWeather(htmlWebPage):
    """
    Formats the text and displays the weather info.
    """
    soup = bs4.BeautifulSoup(htmlWebPage.text, "lxml")
    # display header
    print (' Weather Details '.center(35,'*'))
    # select element with class 'location-name'
    locationName = soup.select('.location-name')
    print ('{0} {1}'.format("Location :".rjust(15), locationName[0].getText().strip()))
    # select elemet with class 'current-temp'
    currentTemp = soup.select('.current-temp')
    print ('{0} {1}C'.format("Current temp :".rjust(15), currentTemp[0].getText().strip()))
    # select element with class 'feels-like' and the element <p> within it
    feelsLike = soup.select('.feels-like p')
    print ('{0} {1}'.format("Feels like :".rjust(15), feelsLike[0].getText()))
    # select element with class 'current-time'
    observedTime = soup.select('.current-time')
    print ('[Observed at : {0}]'.format(' '.join(observedTime[0].getText().split())))
    
# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()
