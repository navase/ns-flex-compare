import os
from dotenv import load_dotenv
from flask import Flask, render_template
import locale
import requests

load_dotenv()
locale.setlocale(locale.LC_ALL, 'nl_NL')
app = Flask(__name__)


@app.route('/')
def index():
    # Get price from nijmegen to utrecht from ns api
    url = 'https://gateway.apiportal.ns.nl/public-prijsinformatie/prices?fromStation=Nijmegen&toStation=Utrecht'
    headers = {'Ocp-Apim-Subscription-Key': os.environ.get('PUBLIC_PRICE_INFORMATION_KEY')}
    response = requests.get(url, headers=headers)
    data = response.json()

    # Select only the prices for a single fare in second class
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

    return render_template('index.html', prices=prices)

