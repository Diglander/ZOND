#независимый модуль класса БД, 
#чтобы не конфликтивоал app.py и service.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class RateHistory(db.Model):# CHECK!!!
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.Date, nullable = False)
    source_api = db.Column(db.String(20), nullable = False)
    currency_code = db.Column(db.String(3), nullable=False)
    rate_vs_usd = db.Column(db.Float, nullable=False)