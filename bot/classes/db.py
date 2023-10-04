import os
import pandas as pd
# Local files
from constants import *

class DB:

    @staticmethod
    def create_db():
        """Create the db if some file is missing"""
        db_dir=os.getenv(DB_DIR) 
        subscription_path=os.getenv(SUBS_DB_PATH) 
        # Database folder does not exist
        if not os.path.exists(db_dir):
            print("The db folder does not exit, creating...")
            os.mkdir(db_dir)
        # CSV file does not exist
        if not os.path.exists(subscription_path):
            print("The subscription file does not exist, creating...")
            data = {'chat_id': []}
            # create a dataframe from the dictionary
            df = pd.DataFrame(data)
            # write dataframe to csv file
            df.to_csv(subscription_path, index=False)

    @staticmethod
    def get_subscription_list():
        """Get all the user ids of subscribers"""
        # Get the path of the csv file
        subscription_path=os.getenv(SUBS_DB_PATH)
        data = pd.read_csv(subscription_path)
        mssid_list = data['chat_id'].tolist()
        return list(dict.fromkeys(mssid_list))