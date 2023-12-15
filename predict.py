from json_connect import *
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta

def predict_tomorrow():
    try:
        data = load_from_json()

        # Extract features (X) and target variable (y)
        dates = [datetime.fromisoformat(entry["datetime"]).timestamp() for entry in data]
        temperatures = [entry["main"]["temp"] for entry in data]

        # Reshape the data
        X = np.array(dates).reshape(-1, 1)
        y = np.array(temperatures)

        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Create a linear regression model
        model = LinearRegression()

        # Train the model
        model.fit(X_train, y_train)

        # Predict tomorrow's temperature
        tomorrow_date = datetime.now() + timedelta(days=1)
        tomorrow_timestamp = tomorrow_date.timestamp()
        tomorrow_temperature = model.predict([[tomorrow_timestamp]])

        
        print(f"Predicted temperature for tomorrow: {tomorrow_temperature[0]} °F")
        return f"Predicted temperature for tomorrow: {tomorrow_temperature[0]} °F"
    except Exception as e:
        print(f"An error occurred while predicting tomorrow's temperature: {e}")
        return f"An error occurred while predicting tomorrow's temperature: {e}"