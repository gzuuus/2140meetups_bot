from time import strftime
import os
from constants import *
import pandas as pd

# Get well formated timestamp
def timestamp():
    ts = strftime("%x, %X -")
    return ts

# Get all the user ids of subscribers
def get_subscription_list():
    # Get the environment variable
    db_dir=os.getenv(DB_DIR) 
    subscription_path=os.getenv(SUBS_DB_PATH) 
    if not os.path.exists(db_dir):
        os.mkdir(db_dir)
    data = pd.read_csv(subscription_path)
    mssid_list = data['chat_id'].tolist()
    return list(dict.fromkeys(mssid_list))