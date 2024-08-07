import os
import shutil
from datetime import datetime


def create_folder_if_not_exists(folder_path):
    os.makedirs(folder_path, exist_ok=True)


def get_current_date():
    now = datetime.now()
    date_string = now.strftime("%d_%m_%Y")
    return date_string


def copy_file(source_path, destination_path):
    # Create the destination directory if it doesn't exist
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)

    # Move the file
    shutil.copy(source_path, destination_path)


def delete_file_if_exist(file_path):
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass


def delete_directory_if_exist(directory_path):
    try:
        shutil.rmtree(directory_path)
    except FileNotFoundError:
        pass


def rename_directory(current_path, new_path):
    os.rename(current_path, new_path)
