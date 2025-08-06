from flask import (
    Flask,
    url_for,
    g,
    render_template,
    request,
    redirect
)  # для гибких гиперссылок, хуки и дизайна
from dotenv import load_dotenv  # для чтения api-key′я из .env
import os  # для записи api-key′я из .env
from loguru import logger
import sys  # для вывода логов в консоль
from flask_sqlalchemy import SQLAlchemy
from datetime import date

from api_clients import ExchangeApiClient, CBRFClient
from models import db, RateHistory
from services import setting_rates, force_CBRF, force_API_Exchange

logger.remove()  # удаляем стандартный logger, делаем свой
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

load_dotenv()  # подгрузка .env в область видимости (scope)

app = Flask(__name__)

#Конфигурация базы данных
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app) #Привязка db из modules.py к настоящему app flask`а

API_KEY, CB_API = os.getenv("API_KEY_env"), os.getenv("CB_API_env")
Exchange_Client = ExchangeApiClient(API_KEY)
Cbrf_Client = CBRFClient(CB_API)

@app.before_request
def check_and_load_rates():
        g.rates, g.source = setting_rates(db, RateHistory, Exchange_Client, Cbrf_Client)

@app.route("/")
def intro():
    if g.rates:
        main_currencies = ['RUB', 'CNY', 'EUR', 'GBP'] #Самые частые валюты
        main_list = []
        minor_list = []
        for code in sorted(g.rates.keys()):
            if code in main_currencies:
                main_list.append(code)
            else:
                minor_list.append(code)
    else:
        main_list = []
        minor_list = []
    
    return render_template("index.html", main = main_list, minor = minor_list)


@app.route("/<chosen_code>")
def show_rate(chosen_code):
    code = chosen_code.upper()
    
    if g.rates and g.rates.get(code):
        context = {
            "currency_chosen_code": code, 
            "rate": g.rates.get(code),
            "source": g.source,
            "currency_name": code
            }
        
        return render_template("rate.html", data=context)
    else:
        return render_template("error.html", message="Нет доступа к курсам.")


@app.route("/force_reload/api_exchange")
def force_reload_exchange():
    force_API_Exchange(db, RateHistory, Exchange_Client)
    return redirect(url_for('intro'))


@app.route("/force_reload/cbrf")
def force_reload_cbrf():
    force_CBRF(db, RateHistory, Cbrf_Client)
    return redirect(url_for('intro'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all() #обеспечиваем доступ к db перед запуском
    app.run(debug=True)