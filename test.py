from app import app
from test_methods import add_two_symbols, divide_two_symbols, get_list, get_weather
import pytest
from models import User
from unittest.mock import patch

def test_index():
    client = app.test_client()
    response = client.get('/')
    print (response.data)
    # assert response.status_code == 200
    assert b'login' in response.data

def test_add_two_symbols():
    assert add_two_symbols(6,7) == 13
    

def test_add_two_symbols_negative():
    assert add_two_symbols(-6,-7) == -13


    
def test_divide_two_symbols():
    assert divide_two_symbols(6, 3) == 2

def test_divide_two_symbols_with_zero():
    with pytest.raises(ZeroDivisionError):
        divide_two_symbols(6, 0)

def test_user_creation():
    user = User(username="Denyska")
    assert user.username == "Denyska"

def test_return_json():
    client = app.test_client()
    response = client.get('/return_json')
    data = response.get_json()
    assert data["bmw"] == 5

def test_list():
    assert len(get_list()) == 2
    assert "biba" in get_list() 

def test_custom_login_failed():
    client = app.test_client()
    response = client.post(
        "/custom_login", data={"username":"dima", "password":"1234"}
    )
    assert response.data == b"invalid username or password"

def test_custom_login_success():
    client = app.test_client()
    response = client.post(
        "/custom_login", data={"username":"dog", "password":"cat"}
    )
    assert response.data == b"succesfully login"

@patch("requests.get")
def test_get_weather(mock_get):
    mock_get.return_value.json.return_value={"temperature":"20"}
    data=get_weather()
    assert data.get("temperature")== "20"
    