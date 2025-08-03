from flask import (
    Flask,
    url_for,
    g,
    render_template,
    request
)  # для гибких гиперссылок, хуки и дизайна
from dotenv import load_dotenv  # для чтения api-key′я из .env
import os  # для записи api-key′я из .env
from loguru import logger
import sys  # для вывода логов в консоль
from flask_sqlalchemy import SQLAlchemy
from datetime import date

from api_clients import ExchangeApiClient, CBRFClient
from models import db, RateHistory
from services import setting_rates

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
    return render_template("index.html")


@app.route("/RUB")
def USD_RUB():
    if g.rates and g.rates.get("RUB"):
        context = {"currency_code": "RUB", "rate": g.rates.get("RUB")}
        return render_template("rate.html", data=context)
    else:
        return render_template("error.html", message="Нет доступа к курсу рубля.")


@app.route("/CNY")
def USD_CNY():
    if g.rates and g.rates.get("CNY"):
        context = {"currency_code": "CNY", "rate": g.rates.get("CNY")}
        return render_template("rate.html", data=context)
    else:
        return render_template("error.html", message="Нет доступа к курсу юаня.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all() #обеспечиваем доступ к db перед запуском
    app.run(debug=True)