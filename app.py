from flask import (
    Flask,
    url_for,
    g,
    render_template,
    request
)  # для гибких гиперссылок, хуки и дизайна
from dotenv import load_dotenv  # для чтения api-key′я из .env
import os  # для записи api-key′я из .env
from api_clients import ExchangeApiClient, CBRFClient
from loguru import logger
import sys  # для вывода логов в консоль
from flask_sqlalchemy import SQLAlchemy
from datetime import date

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
db = SQLAlchemy(app)

class RateHistory(db.Model):# CHECK!!!
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.Date, nullable = False)
    source_api = db.Column(db.String(20), nullable = False)
    currency_code = db.Column(db.String(3), nullable=False)
    rate_vs_usd = db.Column(db.Float, nullable=False)

API_KEY, CB_API = os.getenv("EXCHANGE_API_KEY"), os.getenv("CB_API")
Exchange_Client = ExchangeApiClient(API_KEY)


@app.before_request
def check_and_load_rates():
    api_code = "Нет подключенного API"
    today = date.today()
    today_rates = db.session.execute(db.select(RateHistory).filter_by(date=today)).scalars().all()
    if today_rates:
        logger.info(f"Загружаем курсы за {today} для быстродействия")
        rates_dict = {record.currency_code: record.rate_vs_usd for record in today_rates}
        g.rates = rates_dict
        g.source = today_rates[0].source_api #одинаковый API
        return
    logger.warning(f"В БД не найдено курсов за {today}, подключаемся к API")
    logger.info(f"Входящий запрос на {request.path} для получения курсов.")
    Exchange_Client.fetch_rates()
    if Exchange_Client.success:
        logger.info("Успех! Используются данные от ExchangeApi.")
        g.rates = Exchange_Client.rates
        api_code = "ExchangeAPI"
    else:
        logger.warning(
            "Не удалось связаться с основным API (ExchangeApi)."
            "Пробуем соединиться с API ЦБ РФ."
        )
        Cbrf_Client = CBRFClient(CB_API)
        Cbrf_Client.fetch_rates()
        if Cbrf_Client.success:
            logger.info("Успешно используются данные ЦБ РФ!")
            g.rates = Cbrf_Client.rates
            api_code = "ЦБ РФ"
        else:
            logger.error("Не удалось подключиться ни к одному API!")
            g.rates = None
    if g.rates:
        logger.info(f'Получены {len(g.rates)} курсов от {api_code}. Сохраняем в БД...')
        for rate_code, rate in g.rates.items():
            new_record = RateHistory(
                date = today,
                source_api = api_code,
                currency_code = rate_code,
                rate_vs_usd = rate
            )
            db.session.add(new_record)
        db.session.commit()
        logger.info("Данные успешно сохранены в БД")

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