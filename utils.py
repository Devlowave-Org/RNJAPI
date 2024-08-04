import os
from datetime import datetime


def create_folder_if_not_exists(folder_path):
    os.makedirs(folder_path, exist_ok=True)


def get_current_date():
    now = datetime.now()
    date_string = now.strftime("%d_%m_%Y")
    return date_string
