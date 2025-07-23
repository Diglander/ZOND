import requests
import xml.etree.ElementTree as ET
#Аргументы api_key и  CB_API экспортируются из .env в исполняемом файле
class ExchangeApiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.rates = {}
        self.success = False
        self.full_url = None
    
    def fetch_rates(self):
        self.full_url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/latest/USD"
        try:
            response = requests.get(self.full_url)
            response.raise_for_status() #для правильной работы «try»
            data = response.json()
            if data.get('result') == 'success':
                self.rates = data.get('conversion_rates')
                self.success = True
                
        except requests.exceptions.RequestException as e:
            print(f"ОШИБКА №{e}!!!")
            self.success = False


class CBRFClient:
    def __init__(self, CB_API):
        self.rates = {}
        self.success = False
        self.full_url = CB_API
    
    def fetch_rates(self):
        if not self.full_url:
            print("Не передали классу CBRFClient адрес!")
            self.success = False
            return
        
        try:
            print("Пользуемся ЦБ РФ!")
            temp_rates = {}
            rates_in_rub = {}
            response = requests.get(self.full_url)
            response.raise_for_status() #для правильной работы «try»
            response.encoding = 'windows-1251' #специфика старой кодировки
            root = ET.fromstring(response.text)
            
            for cbr_tag in root.findall('Valute'):
                code = cbr_tag.find('CharCode').text
                cbr_value = cbr_tag.find('Value').text   #|перевод|
                value = float(cbr_value.replace(',','.'))#|перевод|
                nominal = float (cbr_tag.find('Nominal').text)
                rate = value / nominal
                rates_in_rub[code] = rate
                
            for key, value in rates_in_rub.items():
                if key != "USD":
                    temp_rates[key] = round(rates_in_rub[key] / rates_in_rub['USD'], 4)
                    
            temp_rates['RUB'] = round(rates_in_rub['USD'], 4)
            temp_rates['USD'] = 1
            self.rates = temp_rates
            self.success = True
        except requests.exceptions.RequestException as e:
            print(f"ОШИБКА №{e}!!!")
            self.success = False
        except ET.ParseError as e:
            print(f'Парсинг XML ЦБ не удался!: код ошибки {e}')
            self.success = False