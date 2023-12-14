import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import requests
import time
import json
from datetime import datetime, timedelta
import threading

def fetch_weather_data(city, api_key):
    print(city)
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    complete_url = f"{base_url}?q={city}&appid={api_key}"
    response = requests.get(complete_url)
    return response.json()

def save_to_json(data, filename="weather_data.json"):
    try:
        with open(filename, 'r+') as file:
            file_data = json.load(file)
            file_data.append(data)
            file.seek(0)
            json.dump(file_data, file)
    except FileNotFoundError:
        with open(filename, 'w') as file:
            json.dump([data], file)

def load_from_json(filename="weather_data.json"):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def clean_old_data(filename="weather_data.json"):
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

def plot_history(data, time_range, city_name):
    times = [datetime.fromisoformat(entry['datetime']) for entry in data if entry['name'] == city_name]
    temperatures = [entry['main']['temp'] for entry in data if entry['name'] == city_name]

    fig = Figure(figsize=(10, 4))
    plot = fig.add_subplot(111)
    plot.plot(times, temperatures, marker='o')
    plot.set_xlabel('Time')
    plot.set_ylabel('Temperature (K)')
    plot.set_title(f'Weather History in {city_name} - Last {time_range} Hours')
    plot.grid(True)

    return fig

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

def create_gui(api_key):
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
                        f"Description: {current_data['weather'][0]['description']}")
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

    for frame in (current_weather_frame, history_frame):
        frame.grid(row=0, column=0, sticky='nsew')

    current_weather_label = ttk.Label(current_weather_frame, text="", font=("Helvetica", 16))
    current_weather_label.grid(row=0, column=0, padx=20, pady=20)

    control_frame = ttk.Frame(main_frame)
    control_frame.grid(row=1, column=0, sticky='ew')

    ttk.Button(control_frame, text="Current Weather", command=lambda: show_frame(current_weather_frame)).grid(row=0, column=0, padx=5, pady=5)
    ttk.Button(control_frame, text="History", command=lambda: show_frame(history_frame)).grid(row=0, column=1, padx=5, pady=5)
    global city_name
    def on_combobox_selected(event):
        selected_city = combobox.get()
        # Add the following line to update the city_name variable
        global city_name
        city_name = selected_city
        print(f"Selected city: {selected_city}")

    selected_city_var = tk.StringVar()
    cities = ["Ohama", "Paris"]
    combobox = ttk.Combobox(root, textvariable=selected_city_var, values=cities)
    combobox.set(cities[0])  # Default text when the ComboBox is not selected
    combobox.grid(row=0, column=3, padx=10, pady=10)

    def show_frame(frame):
        frame.tkraise()
        if frame == current_weather_frame:
            refresh_current_weather()
        elif frame == history_frame:
            show_history(24)  # Default to 24 hours

    combobox.bind("<<ComboboxSelected>>", on_combobox_selected)

    # Start the GUI with an initial city
    city_name = cities[0]

    show_frame(current_weather_frame)

    threading.Thread(target=update_weather_data, args=(api_key,), daemon=True).start()

    root.mainloop()

def main():
    api_key = "8a7fcee2ba05b7ef550d610a92987411"
    # city_name = input("Enter city name: ")
    create_gui(api_key)

if __name__ == "__main__":
    main()
