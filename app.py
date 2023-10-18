import os
from dotenv import load_dotenv
from flask import Flask, abort, render_template, request
import locale
import requests

load_dotenv()
locale.setlocale(locale.LC_ALL, 'nl_NL')
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        fromStation = request.form.get("fromStation")
        toStation = request.form.get("toStation")

        # Validate that fromStation and toStation are existing stations and not the same station
        if fromStation not in stations() or toStation not in stations() or fromStation == toStation:
            abort(400)

        # Get public price information key from environment variables
        public_price_information_key = os.environ.get('PUBLIC_PRICE_INFORMATION_KEY')

        # Validate that public price information key is set
        if not public_price_information_key:
            abort(401)

        # Get prices from fromStation to toStation from NS API
        url = "https://gateway.apiportal.ns.nl/public-prijsinformatie/prices?fromStation={}&toStation={}".format(fromStation, toStation)
        headers = {'Ocp-Apim-Subscription-Key': public_price_information_key}
        response = requests.get(url, headers=headers)

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
            price['price'] = locale.currency(price['price'] / 100, grouping=True).replace('Eu', '€')
            price['discount'] = price['discountType'].replace('_', ' ').capitalize()

        return render_template('index.html', stations=stations(), prices=prices, fromStation=fromStation, toStation=toStation)

    else:
        return render_template('index.html', stations=stations())


def stations():
    # Get NS app key from environment variables
    ns_app_key = os.environ.get('NS_APP_KEY')

    # Validate that NS app key is set
    if not ns_app_key:
        abort(401)

    # Get list of train stations from NS API
    url = 'https://gateway.apiportal.ns.nl/reisinformatie-api/api/v2/stations?countryCodes=nl'
    headers = {'Ocp-Apim-Subscription-Key': ns_app_key}
    response = requests.get(url, headers=headers)

    # Validate that response is successful
    if response.status_code != 200:
        abort(response.status_code)

    # Select station names
    data = response.json()
    stations = []
    for station in data['payload']:
        stations.append(station['namen']['lang'])

    return sorted(stations)
