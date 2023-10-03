import requests, json
from constants import *

HEAD='HEAD'
GET='GET'
HEADERS = { "Content-Type": "application/json; charset=utf-8" }

def make_request(domain, req_type):
    if req_type == HEAD:
        return requests.head(domain, headers=HEADERS)
    elif req_type == GET:
        return requests.get(domain, headers=HEADERS).json()
