import os, requests, json
from constants import *

HEAD='HEAD'
GET='GET'

# pythonanywhere just allows a http proxy. 
# I guess the proxy server lives in the host
PROXY={"http":"proxy.server:3128"}

HEADERS = { "Content-Type": "application/json; charset=utf-8" }


def make_request(domain, req_type):
    proxy=need_to_proxy()
    if req_type == HEAD:
        return requests.head(domain, headers=HEADERS, proxies=proxy) 
    elif req_type == GET:
        return requests.get(domain, headers=HEADERS, proxies=proxy).json()

# In production, there are a whitelist to make outside server requests but our domain is
# not in that allowed list. For that reason, we need to pass through from their proxy
def need_to_proxy():
    env = os.getenv(ENV)
    if env == PROD:
        return PROXY
    else:
        return {}

