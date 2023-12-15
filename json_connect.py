import json
from datetime import datetime, timedelta
from utils import *

def save_to_json(data, filename=JSON_FILE_NAME):
    try:
        with open(filename, 'r+') as file:
            file_data = json.load(file)
            file_data.append(data)
            file.seek(0)
            json.dump(file_data, file)
    except FileNotFoundError:
        with open(filename, 'w') as file:
            json.dump([data], file)

def load_from_json(filename=JSON_FILE_NAME):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    
def clean_old_data(filename=JSON_FILE_NAME):
    try:
        with open(filename, 'r+') as file:
            file_data = json.load(file)
            cutoff_date = datetime.now() - timedelta(days=3)
            updated_data = [entry for entry in file_data if datetime.fromisoformat(entry['datetime']) > cutoff_date]
            file.seek(0)
            file.truncate()
            json.dump(updated_data, file)
    except FileNotFoundError:
        pass