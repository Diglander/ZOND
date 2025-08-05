import pytest
import json
from api_clients import ExchangeApiClient, CBRFClient

@pytest.fixture
def mock_exchange_json_response(mocker):
    with open("tests/data/exchange_sample.json", "r") as f:
        json_content = f.read()
        json_content = json.loads(json_content)
    
    mock_response = mocker.Mock()
    mock_response.raise_for_status.return_value  = None
    mock_response.json.return_value = json_content
    return mock_response

def test_exchange_parse_correctly(mocker, mock_exchange_json_response):
    mocker.patch("api_clients.requests.get",return_value = mock_exchange_json_response)
    
    exchange_alg = ExchangeApiClient("http://Example.com")
    
    exchange_alg.fetch_rates()
    
    assert exchange_alg.success is True
    assert exchange_alg.rates is not None
    assert exchange_alg.rates['USD'] == 1.0
    assert exchange_alg.rates['RUB'] == 79.8015

@pytest.fixture
def mock_cbr_xml_response(mocker):
    """
    Эта фикстура создает "фальшивый" ответ от requests.get,
    как будто мы сходили в интернет и получили наш эталонный XML.
    """
    # Читаем наш "фальшивый" свиток из файла
    with open("tests/data/cbr_sample.xml", "r", encoding="windows-1251") as f:
        xml_content = f.read()

    # Создаем объект-обманку, который будет притворяться ответом от сервера
    mock_response = mocker.Mock()
    # Говорим, что у этой обманки есть атрибут .text, который содержит наш XML
    mock_response.text = xml_content
    # Говорим, что у нее есть метод .raise_for_status(), который ничего не делает
    mock_response.raise_for_status.return_value = None
    return mock_response

def test_cbrf_parses_correctly(mocker, mock_cbr_xml_response):
    mocker.patch("api_clients.requests.get", return_value = mock_cbr_xml_response)
    
    cbr_alg = CBRFClient("http://Example.com")# URL не важен с mock
    
    cbr_alg.fetch_rates()
    
    assert cbr_alg.success is True
    assert cbr_alg.rates is not None
    assert cbr_alg.rates['USD'] == 1.0
    assert cbr_alg.rates['RUB'] == 80.3289