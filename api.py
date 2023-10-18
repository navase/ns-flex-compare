from os import environ
from flask import abort
from requests import get
from locale import currency

def stations():
    # Get NS app key from environment variables
    ns_app_key = environ.get('NS_APP_KEY')

    # Validate that NS app key is set
    if not ns_app_key:
        abort(401)

    # Get list of train stations from NS API
    url = 'https://gateway.apiportal.ns.nl/reisinformatie-api/api/v2/stations?countryCodes=nl'
    headers = {'Ocp-Apim-Subscription-Key': ns_app_key}
    response = get(url, headers=headers)

    # Validate that response is successful
    if response.status_code != 200:
        abort(response.status_code)

    # Select station names
    data = response.json()
    stations = []
    for station in data['payload']:
        stations.append(station['namen']['lang'])

    return sorted(stations)


def prices(fromStation, toStation):
    # Get public price information key from environment variables
        public_price_information_key = environ.get('PUBLIC_PRICE_INFORMATION_KEY')

        # Validate that public price information key is set
        if not public_price_information_key:
            abort(401)

        # Get prices from fromStation to toStation from NS API
        url = "https://gateway.apiportal.ns.nl/public-prijsinformatie/prices?fromStation={}&toStation={}".format(fromStation, toStation)
        headers = {'Ocp-Apim-Subscription-Key': public_price_information_key}
        response = get(url, headers=headers)

        # Validate that response is successful
        if response.status_code != 200:
            abort(response.status_code)

        # Select only the prices for a single fare in second class
        data = response.json()
        prices = []
        for price_option in data['priceOptions']:
            if price_option['type'] == 'ROUTE_WITHOUT_OPTIONS':
                for total_price in price_option['totalPrices']:
                    if total_price['classType'] == 'SECOND' and total_price['productType'] == 'SINGLE_FARE':
                        prices.append(total_price)

        # Sort by price, lowest first
        prices = sorted(prices, key=lambda k: k['price'])

        # Format price in euros and discount as text
        for price in prices:
            price['price'] = currency(price['price'] / 100, grouping=True).replace('Eu', '€')
            price['discount'] = price['discountType'].replace('_', ' ').capitalize()

        return prices
