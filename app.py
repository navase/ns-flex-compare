from dotenv import load_dotenv
from flask import Flask, abort, render_template, request
import locale

import api

load_dotenv()
locale.setlocale(locale.LC_ALL, 'nl_NL')
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        fromStation = request.form.get("fromStation")
        toStation = request.form.get("toStation")

        # Validate that fromStation and toStation are existing stations and not the same station
        if fromStation not in api.stations() or toStation not in api.stations() or fromStation == toStation:
            abort(400)

        prices = api.prices(fromStation, toStation)

        return render_template('index.html', stations=api.stations(), prices=prices, fromStation=fromStation, toStation=toStation)

    else:
        return render_template('index.html', stations=api.stations())


