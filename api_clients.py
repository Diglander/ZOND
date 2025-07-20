import requests
class ExchangeAPI:
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