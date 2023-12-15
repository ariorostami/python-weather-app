import requests
import time
from datetime import datetime, timedelta
from loguru import logger
from json_connect import *
from predict import *
from json_connect import *
from predict import *
import threading
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from weather import *

def fetch_weather_data(city, api_key):
    print(city)
    base_url = API_URL
    complete_url = f"{base_url}?q={city}&appid={api_key}"
    # response = requests.get(complete_url)
    # return response.json()
    try:
        response = requests.get(complete_url)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Successful response. Data: {str(data)[:100]}")
            return data
        else:
            logger.warning(f"Failed to fetch weather data. Status code: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"An error occurred while fetching weather data: {e}")
        return None


def kelvin_to_fahrenheit(kelvin):
    fahrenheit = (kelvin - 273.15) * 9/5 + 32
    return fahrenheit

def update_weather_data(api_key):
    global city_name
    while True:
        weather_data = fetch_weather_data(city_name, api_key)
        if weather_data.get("cod") == 200:
            weather_data['main']['temp'] = kelvin_to_fahrenheit(weather_data['main']['temp'])
            weather_data['datetime'] = datetime.now().isoformat()
            save_to_json(weather_data)
            print_new_reading(weather_data)
        clean_old_data()
        last_data = load_from_json()
        if last_data:
            last_entry = last_data[-1]
            last_update_time = datetime.fromisoformat(last_entry['datetime'])
            next_update_time = last_update_time + timedelta(minutes=1)
            current_time = datetime.now()
            if current_time >= next_update_time:
                wait_time = 0
            else:
                wait_time = (next_update_time - current_time).total_seconds()
        else:
            wait_time = 0  # If no data is present, fetch immediately

        time.sleep(wait_time)
        

def print_new_reading(data):
    print("\nNew Weather Data Received:")
    print(f"City: {data['name']}")
    print(f"Temperature: {data['main']['temp']} °F")
    print(f"Pressure: {data['main']['pressure']} hPa")
    print(f"Humidity: {data['main']['humidity']}%")
    print(f"Description: {data['weather'][0]['description']}")
    print(f"Time: {data['datetime']}")


def plot_history(data, time_range, city_name):
    times = [datetime.fromisoformat(entry['datetime']) for entry in data if entry['name'] == city_name]
    temperatures = [entry['main']['temp'] for entry in data if entry['name'] == city_name]

    fig = Figure(figsize=(10, 4))
    plot = fig.add_subplot(111)
    plot.plot(times, temperatures, marker='o')
    plot.set_xlabel('Time')
    plot.set_ylabel('Temperature (F)')
    plot.set_title(f'Weather History in {city_name} - Last {time_range} Hours')
    plot.grid(True)

    return fig

def create_gui(api_key, ):
    def show_predict_tomorrow_frame():
        predict_text = predict_tomorrow()
        tomorrow_weather_label.config(text=predict_text)

    def refresh_current_weather():
        last_data = load_from_json()
        if last_data:
            valid_data = [data for data in last_data if data.get("cod") == 200 and data['name'] == city_name]
            if valid_data:
                current_data = valid_data[-1]
                text = (f"City: {city_name}\n"
                        f"Temperature: {current_data['main']['temp']} F\n"
                        f"Pressure: {current_data['main']['pressure']} hPa\n"
                        f"Humidity: {current_data['main']['humidity']}%\n"
                        f"Description: {current_data['weather'][0]['description']}\n\n")
                current_weather_label.config(text=text)

    def show_history(time_range):
        for widget in history_frame.winfo_children():
            widget.destroy()
        data = load_from_json()
        fig = plot_history(data, time_range, city_name)
        canvas = FigureCanvasTkAgg(fig, master=history_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    root = tk.Tk()
    root.title("Weather Data Application")

    main_frame = ttk.Frame(root)
    main_frame.grid(row=0, column=0, sticky='nsew')

    current_weather_frame = ttk.Frame(main_frame)
    history_frame = ttk.Frame(main_frame)
    predict_tomorrow_frame = ttk.Frame(main_frame)

    for frame in (current_weather_frame, history_frame, predict_tomorrow_frame):
        frame.grid(row=0, column=0, sticky='nsew')

    current_weather_label = ttk.Label(current_weather_frame, text="", font=("Helvetica", 16))
    current_weather_label.grid(row=0, column=0, padx=20, pady=20)

    tomorrow_weather_label = ttk.Label(predict_tomorrow_frame, text="", font=("Helvetica", 16))
    tomorrow_weather_label.grid(row=0, column=0, padx=20, pady=20)

    control_frame = ttk.Frame(main_frame)
    control_frame.grid(row=1, column=0, sticky='ew')

    ttk.Button(control_frame, text="Current Weather", command=lambda: show_frame(current_weather_frame)).grid(row=0, column=0, padx=5, pady=5)
    ttk.Button(control_frame, text="History", command=lambda: show_frame(history_frame)).grid(row=0, column=1, padx=5, pady=5)
    ttk.Button(control_frame, text="Predict Tomorrow", command=lambda: show_frame(predict_tomorrow_frame)).grid(row=0, column=2, padx=5, pady=5)

    global city_name

    def fetch_and_update_weather_for_city(city):
        weather_data = fetch_weather_data(city, api_key)
        if weather_data.get("cod") == 200:
            weather_data['main']['temp'] = kelvin_to_fahrenheit(weather_data['main']['temp'])
            weather_data['datetime'] = datetime.now().isoformat()
            save_to_json(weather_data)
            print_new_reading(weather_data)
            refresh_current_weather()

    def on_combobox_selected(event):
        global city_name
        selected_city = combobox.get()
        city_name = selected_city

        last_data = load_from_json()
        if not any(entry.get('name') == city_name for entry in last_data):
            fetch_and_update_weather_for_city(city_name)

        show_frame(current_weather_frame)

    selected_city_var = tk.StringVar()
    cities = load_cities_from_json()  # Load cities from JSON file
    combobox = ttk.Combobox(control_frame, textvariable=selected_city_var, values=cities)
    combobox.set(cities[0])  # Default text when the ComboBox is not selected
    combobox.grid(row=0, column=3, padx=5, pady=5)
    combobox.bind("<<ComboboxSelected>>", on_combobox_selected)

    def handle_city_search(event=None):
        new_city = city_search_var.get().strip()
        if new_city and new_city not in cities:
            cities.append(new_city)
            combobox.config(values=cities)
            save_cities_to_json(cities)  # Save cities list to JSON
        combobox.set(new_city)
        global city_name
        city_name = new_city
        last_data = load_from_json()
        if not any(entry.get('name') == city_name for entry in last_data):
            fetch_and_update_weather_for_city(city_name)
        show_frame(current_weather_frame)

    city_search_label = ttk.Label(control_frame, text="City Search:")
    city_search_label.grid(row=0, column=4, padx=5, pady=5)

    city_search_var = tk.StringVar()
    city_search_entry = ttk.Entry(control_frame, textvariable=city_search_var)
    city_search_entry.grid(row=0, column=5, padx=5, pady=5)
    city_search_entry.bind("<Return>", handle_city_search)  # Bind the Enter key

    search_button = ttk.Button(control_frame, text="Search", command=handle_city_search)
    search_button.grid(row=0, column=6, padx=5, pady=5)

    def show_frame(frame):
        frame.tkraise()
        if frame == current_weather_frame:
            refresh_current_weather()
        elif frame == history_frame:
            show_history(24)  # Default to 24 hours
        elif frame == predict_tomorrow_frame:
            show_predict_tomorrow_frame()

    city_name = cities[0]
    show_frame(current_weather_frame)

    threading.Thread(target=update_weather_data, args=(api_key,), daemon=True).start()

    root.mainloop()



def save_cities_to_json(cities, filename="cities.json"):
    with open(filename, 'w') as file:
        json.dump(cities, file)

def load_cities_from_json(filename="cities.json"):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return ["Ohama", "Paris"]  # Default cities


