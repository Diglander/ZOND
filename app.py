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


logger.remove  # удаляем стандартный logger, делаем свой
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)


load_dotenv()  # подгрузка .env в область видимости (scope)

app = Flask(__name__)

API_KEY, CB_API = os.getenv("EXCHANGE_API_KEY"), os.getenv("CB_API")
Exchange_Client = ExchangeApiClient(API_KEY)


@app.before_request
def load_rates():
    logger.info(f"Входящий запрос на {request.path} для получения курсов.")

    Exchange_Client.fetch_rates()
    if Exchange_Client.success:
        logger.info("Успех! Используются данные от ExchangeApi.")
        g.rates = Exchange_Client.rates
        return
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
        else:
            logger.error("Не удалось подключиться ни к одному API!")
            g.rates = None


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
    app.run(debug=True)
