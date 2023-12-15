from dotenv import load_dotenv
import os

load_dotenv()
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/weather_app.log")
JSON_FILE_NAME = os.getenv("JSON_FILE_NAME", "weather_data.json")
API_KEY = os.getenv("API_KEY", "YOUR_DEFAULT_API_KEY")
API_URL = os.getenv("API_URL", "http://api.openweathermap.org/data/2.5/weather")
CITIES_FILE_NAME = os.getenv("CITIES_FILE_NAME", "cities.json")