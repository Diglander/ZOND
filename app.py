from flask import Flask, url_for #для гибких гиперссылок в HTML-странице
import requests
from dotenv import load_dotenv # для чтения api-key′я из .env
import os # для записи api-key′я из .env

load_dotenv() #подгрузка .env в область видимости (scope)

app = Flask(__name__)

API_KEY = os.getenv('EXCHANGE_API_KEY')

full_url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"

def get_rates_from_exchange():
    try:
        response = requests.get(full_url)
        response.raise_for_status() #для правильной работы «try»
        data = response.json()
        
        if data.get('result') == 'success':
            return data.get('conversion_rates')
    except:
        print("ОШИБКА!!!")
        return None #чтобы сделать проверку на корректность в декораторах 


@app.route('/')
def intro():
    return f"""
<h1>Привет! Выбирай что хочешь!</h1> 
<p><a href="{url_for('USD_RUB')}"> Рубль</p>
<p><a href="{url_for('USD_CNY')}"> Юань</p>
""" #использовали url_for для гиперссылок

@app.route('/RUB')
def USD_RUB():
    rates = get_rates_from_exchange()
    if rates:
        return f'<h1><a href="{url_for('intro')}"> В 1 долларе {rates['RUB']} рублей</h1>'
    else:
        return "<h1>Ошибка</h1>"

@app.route('/CNY')
def USD_CNY():
    rates = get_rates_from_exchange()
    if rates:
        return f'<h1><a href="{url_for('intro')}"> В 1 долларе {rates['CNY']} юаней</h1>'
    else:
        return "<h1>Ошибка</h1>"

if __name__ == '__main__':
    app.run(debug=True)