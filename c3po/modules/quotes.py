#! /usr/bin/env python3
import requests
import json

def get_star_wars_quote():
    url = 'http://swquotesapi.digitaljedi.dk/api/SWQuote/RandomStarWarsQuote'
    response = requests.get(url)
    return response.json()
