import pytest
import numpy as np
import requests
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tasks.task_manager import *

def test_clean_missing_data():
    data = np.array([
        ['Johnny', 'Rocker'],
        ['V', None],
        [None, 'Netrunner']
    ])
    cleaned = clean_missing_data(data)
    assert all(None not in row for row in cleaned)

def test_filter_by_class():
    data = np.array([
        ['Johnny', 'Rocker'],
        ['V', 'Solo'],
        ['T-Bug', 'Netrunner']
    ])
    filtered = filter_by_class(data, 'Netrunner')
    assert filtered.shape[0] == 1
    assert filtered[0][0] == 'T-Bug'

def test_get_long_names():
    data = np.array([
        ['JohnnySilverhand', 'Rocker'],
        ['V', 'Solo'],
        ['T-Bug', 'Netrunner']
    ])
    names = get_long_names(data)
    assert names == ['JohnnySilverhand']

def test_uppercase_names():
    data = np.array([
        ['Johnny', 'Rocker'],
        ['v', 'Solo']
    ])
    uppercased = uppercase_names(data)
    assert uppercased[0][0] == 'JOHNNY'

def test_fetch_character_api_data(monkeypatch):
    class MockResponse:
        status_code = 200
        def json(self):
            return {'characters': [{'name': 'V'}, {'name': 'Johnny'}]}
    
    monkeypatch.setattr(requests, "get", lambda url: MockResponse())
    response = fetch_character_api_data("http://fake.api/characters")
    assert response.status_code == 200

def test_validate_api_response():
    response = requests.Response()
    response.status_code = 200
    assert validate_api_response(response) == True
    response.status_code = 404
    assert validate_api_response(response) == False

def test_extract_names_from_api():
    json_data = {'characters': [{'name': 'V'}, {'name': 'Johnny'}]}
    names = extract_names_from_api(json_data)
    assert names == ['V', 'Johnny']

def test_clean_special_characters():
    s = "Hello@Cyber#punk!"
    cleaned = clean_special_characters(s)
    assert cleaned == "HelloCyberpunk"

def test_merge_local_and_api_data():
    local_data = np.array([['Johnny', 'Rocker']])
    api_data = ['V', 'T-Bug']
    merged = merge_local_and_api_data(local_data, api_data)
    assert len(merged) == 3

def send_post_request(url: str, data: dict, headers: dict = None):
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # hata varsa exception fırlatır
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status Code: {response.status_code}")
    except Exception as err:
        print(f"Other error occurred: {err}")

class ResultCollector:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            if report.passed:
                self.passed += 1
            elif report.failed:
                self.failed += 1

def run_tests():
    collector = ResultCollector()
    pytest.main(["tests"], plugins=[collector])
    print(f"\nToplam Başarılı: {collector.passed}")
    print(f"Toplam Başarısız: {collector.failed}")
    
    user_score = (collector.passed / (collector.passed + collector.failed)) * 100
    print(round(user_score, 2))
    
    url = "https://kaizu-api-8cd10af40cb3.herokuapp.com/projectLog"
    payload = {
        "user_id": 518,
        "project_id": 266,
        "user_score": round(user_score, 2),
        "is_auto": False
    }
    headers = {
        "Content-Type": "application/json"
    }
    send_post_request(url, payload, headers)

if __name__ == "__main__":
    run_tests()
