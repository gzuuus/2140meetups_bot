from time import strftime
import os
from constants import *
import pandas as pd

# Get well formated timestamp
def timestamp():
    ts = strftime("%x, %X -")
    return ts