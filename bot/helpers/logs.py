from helpers.utils import *

def display_log(message, moment=False):
    if moment:
        message = f"{timestamp()} {message}"
    print(message)