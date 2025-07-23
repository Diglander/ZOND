from flask import Flask, url_for, g #для гибких гиперссылок, хуки
import requests
from dotenv import load_dotenv # для чтения api-key′я из .env
import os # для записи api-key′я из .env
from api_clients import ExchangeApiClient, CBRFClient

load_dotenv() #подгрузка .env в область видимости (scope)

app = Flask(__name__)

API_KEY, CB_API = os.getenv('EXCHANGE_API_KEY'), os.getenv("CB_API")

Exchange_Client = ExchangeApiClient(API_KEY)

@app.before_request
def load_rates():
    Exchange_Client.fetch_rates()
    if Exchange_Client.success:
        g.rates = Exchange_Client.rates
    else:
        Cbrf_Client = CBRFClient(CB_API)
        Cbrf_Client.fetch_rates()
        if Cbrf_Client.success:
            g.rates = Cbrf_Client.rates
        else:
            print ("Не удалось подключиться ни к одному API!")

@app.route('/')
def intro():
    return f"""
<h1>Привет! Выбирай что хочешь!</h1> 
<p><a href="{url_for('USD_RUB')}"> Рубль</a></p>
<p><a href="{url_for('USD_CNY')}"> Юань</a></p>
""" #использовали url_for для гиперссылок

@app.route('/RUB')
def USD_RUB():
    if (g.rates and g.rates.get('RUB')):
        return f'<h1><a href="{url_for('intro')}"> В 1 долларе {g.rates.get('RUB')} рублей</h1>'
    else:
        return "<h1>Ошибка</h1>"

@app.route('/CNY')
def USD_CNY():
    if (g.rates and g.rates.get('CNY')):
        return f'<h1><a href="{url_for('intro')}"> В 1 долларе {g.rates.get('CNY')} юаней</h1>'
    else:
        return "<h1>Ошибка</h1>"

if __name__ == '__main__':
    app.run(debug=True)