#!/usr/bin/env python3
"""
Hardened getBomWeather.py:
- uses timeouts and catches RequestException
- safe HTML selection with select_one
- fetchCityInfo returns [] when not available
"""

import requests
import bs4
import sys
import datetime
import json
import logging

DEFAULT_TIMEOUT = 10
logger = logging.getLogger("getBomWeather")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main():
    states = ["vic", "nsw", "wa", "sa", "nt", "tas"]
    try:
        if len(sys.argv) == 1:
            cityInput = input("Enter City name (replace any spaces with a hyphen) or postcode: ")
            if cityInput.isnumeric():
                processPostcode(cityInput)
            else:
                stateInput = input("Enter State code (choose from VIC, NSW, WA, SA, NT, TAS): ")
                if stateInput.lower() not in states:
                    print("WARNING : Invalid choice!")
                    sys.exit(0)
                print("Fetching weather... ")
                result = fetchBomWeather(stateInput, cityInput)
                if result is not None:
                    displayWeather(result)
        elif len(sys.argv) == 3:
            stateInput = sys.argv[1]
            cityInput = sys.argv[2]
            if stateInput.lower() not in states:
                print("Invalid State code supplied. Please choose from (VIC, NSW, WA, SA, NT, TAS).")
                sys.exit(0)
            result = fetchBomWeather(stateInput, cityInput)
            if result is not None:
                displayWeather(result)
        else:
            print("[{:%d/%m/%Y %I:%M:%S %p}] Usage: {} <state> <city>".format(datetime.datetime.now(), sys.argv[0]))
            sys.exit(0)
    except KeyboardInterrupt:
        print("\nExiting.")
        sys.exit(0)


def processPostcode(cityInput):
    cityName = ""
    stateCode = ""
    postCode = int(cityInput)
    cityInfo = fetchCityInfo(postCode)

    if not cityInfo:
        print("Invalid postcode or no data available!")
        return

    if len(cityInfo) == 1:
        cityName = cityInfo[0]["name"].lower().replace(" ", "-")
        stateCode = cityInfo[0]["state"]["abbreviation"].lower()
        print("Fetching weather... ")
        result = fetchBomWeather(stateCode, cityName)
        if result is not None:
            displayWeather(result)
    else:
        print("Multiple locations found!")
        for idx, n in enumerate(cityInfo, start=1):
            print(f"{idx}. {n['name']}")
        while True:
            userChoice = input("Select a number from above (0 to quit) : ")
            if userChoice.isnumeric():
                choice = int(userChoice)
                if choice == 0:
                    break
                if 1 <= choice <= len(cityInfo):
                    cityName = cityInfo[choice - 1]["name"].lower().replace(" ", "-")
                    stateCode = cityInfo[choice - 1]["state"]["abbreviation"].lower()
                    result = fetchBomWeather(stateCode, cityName)
                    if result is not None:
                        displayWeather(result)
                    break


def fetchCityInfo(postCode):
    header = {"Content-Type": "application/json"}
    api_url = f"http://v0.postcodeapi.com.au/suburbs/{postCode}.json"
    try:
        response = requests.get(api_url, headers=header, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        logger.warning("Failed to fetch city info for postcode %s: %s", postCode, exc)
        return []


def fetchBomWeather(stateInput, cityInput):
    url = f"http://m.bom.gov.au/{stateInput}/{cityInput}/"
    try:
        res = requests.get(url, timeout=DEFAULT_TIMEOUT)
        res.raise_for_status()
    except requests.exceptions.RequestException:
        print("WARNING : Invalid City name or network error. Please try again.")
        return None

    return res


def displayWeather(htmlWebPage):
    soup = bs4.BeautifulSoup(htmlWebPage.text, "lxml")
    print(" Weather Details ".center(35, "*"))

    location = soup.select_one(".location-name")
    current_temp = soup.select_one(".current-temp")
    feels_like = soup.select_one(".feels-like p")
    observed_time = soup.select_one(".current-time")

    if location:
        print(f"{'Location :'.rjust(15)} {location.get_text().strip()}")
    else:
        print("Location : n/a")

    if current_temp:
        print(f"{'Current temp :'.rjust(15)} {current_temp.get_text().strip()}C")
    else:
        print("Current temp : n/a")

    if feels_like:
        print(f"{'Feels like :'.rjust(15)} {feels_like.get_text().strip()}")
    else:
        print("Feels like : n/a")

    if observed_time:
        print(f"[Observed at : {' '.join(observed_time.get_text().split())}]")
    else:
        print("Observed at : n/a")


if __name__ == "__main__":
    main()
