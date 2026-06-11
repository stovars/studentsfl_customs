import requests
def add_two_symbols(a, b):
    return(a+b)

def divide_two_symbols(a,b):
    return(a/b)

def get_list():
    return["biba","boba"]

def get_weather():
    response=requests.get("https://api.weather.com")
    return response.json()