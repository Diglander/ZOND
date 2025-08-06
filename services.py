from loguru import logger
from datetime import date
from flask_sqlalchemy import SQLAlchemy
from api_clients import ExchangeApiClient, CBRFClient

def setting_rates(
    db: SQLAlchemy,
    RateHistory: type,
    Exchange_Client: ExchangeApiClient,
    Cbrf_Client: CBRFClient
) -> tuple[dict | None, str]:
    rates = {}
    api_code = "Нет подключенного API"
    today = date.today()
    today_rates = db.session.execute(db.select(RateHistory).filter_by(date=today)).scalars().all()
    if today_rates:
        logger.info(f"Загружаем курсы за {today} для быстродействия")
        rates_dict = {record.currency_code: record.rate_vs_usd for record in today_rates}
        return rates_dict, today_rates[0].source_api
    logger.warning(f"В БД не найдено курсов за {today}, подключаемся к API")
    
    logger.info("Входящий запрос к ExchangeAPI для получения курсов.")
    Exchange_Client.fetch_rates()
    if Exchange_Client.success:
        logger.info("Успех! Используются данные от ExchangeApi.")
        rates = Exchange_Client.rates
        api_code = "ExchangeAPI"
        
    else:
        logger.warning(
            "Не удалось связаться с основным API (ExchangeApi)."
            "Пользуемся API от ЦБ РФ."
        )
        Cbrf_Client.fetch_rates()
        if Cbrf_Client.success:
            logger.info("Успешно используются данные ЦБ РФ!")
            rates = Cbrf_Client.rates
            api_code = "ЦБ РФ"
        else:
            logger.error("Не удалось подключиться ни к одному API!")
            
    if rates:
        logger.info(f'Получены {len(rates)} курсов от {api_code}. Сохраняем в БД...')
        for rate_code, rate in rates.items():
            new_record = RateHistory(
                date = today,
                source_api = api_code,
                currency_code = rate_code,
                rate_vs_usd = rate
            )
            db.session.add(new_record)
        db.session.commit()
        logger.info("Данные успешно сохранены в БД")
    return rates, api_code


def force_API_Exchange(
    db: SQLAlchemy,
    RateHistory: type,
    Exchange_Client: ExchangeApiClient,
):
    logger.info("ПРИНУДИТЕЛЬНЫЙ ЗАПРОС к ExchangeAPI.")
    Exchange_Client.fetch_rates()
    if Exchange_Client.success:
        logger.info("Успех! Сохраняем данные от ExchangeApi.")
        today = date.today()
        # Удаляем старые записи за сегодня, если они были от другого источника
        RateHistory.query.filter_by(date=today).delete()
        for rate_code, rate in Exchange_Client.rates.items():
            new_record = RateHistory(
                date=today,
                source_api="ExchangeAPI",
                currency_code=rate_code,
                rate_vs_usd=rate
            )
            db.session.add(new_record)
        db.session.commit()
        logger.info("Данные успешно сохранены в БД")
    else:
        logger.error("Принудительный запрос к ExchangeAPI провалился.")


def force_CBRF(
    db: SQLAlchemy,
    RateHistory: type,
    Cbrf_Client: CBRFClient
):
    logger.info("ПРИНУДИТЕЛЬНЫЙ ЗАПРОС к ЦБ РФ.")
    Cbrf_Client.fetch_rates()
    if Cbrf_Client.success:
        logger.info("Успех! Сохраняем данные от ЦБ РФ.")
        today = date.today()
        # Удаляем старые записи за сегодня, если они были от другого источника
        RateHistory.query.filter_by(date=today).delete()
        for rate_code, rate in Cbrf_Client.rates.items():
            new_record = RateHistory(
                date=today,
                source_api="ЦБ РФ",
                currency_code=rate_code,
                rate_vs_usd=rate
            )
            db.session.add(new_record)
        db.session.commit()
        logger.info("Данные успешно сохранены в БД")
    else:
        logger.error("Принудительный запрос к ЦБ РФ провалился.") 