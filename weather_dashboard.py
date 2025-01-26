import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import io
import urllib.request


class WeatherDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Weather Dashboard")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f0f0")

        # API Key for OpenWeatherMap
        self.api_key = "YOUR_API_KEY_HERE"  # Replace with your API key

        # Store weather data
        self.weather_data = None
        self.forecast_data = None

        self.setup_gui()

    def setup_gui(self):
        # Search Frame
        search_frame = tk.Frame(self.root, bg="#f0f0f0")
        search_frame.pack(pady=20)

        self.city_entry = tk.Entry(search_frame, font=("Helvetica", 14), width=30)
        self.city_entry.pack(side=tk.LEFT, padx=10)
        self.city_entry.insert(0, "Enter city name...")
        self.city_entry.bind("<FocusIn>", lambda e: self.city_entry.delete(0, tk.END))

        search_button = tk.Button(
            search_frame,
            text="Search",
            command=self.get_weather,
            font=("Helvetica", 12),
            bg="#4CAF50",
            fg="white",
            padx=20
        )
        search_button.pack(side=tk.LEFT)

        # Main Content Frame
        self.content_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        # Current Weather Frame
        self.current_weather_frame = tk.Frame(self.content_frame, bg="white", relief=tk.RAISED, bd=2)
        self.current_weather_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        # Forecast Frame
        self.forecast_frame = tk.Frame(self.content_frame, bg="white", relief=tk.RAISED, bd=2)
        self.forecast_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

    def get_weather(self):
        city = self.city_entry.get()

        # Get current weather
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={self.api_key}&units=metric"

        try:
            # Get current weather data
            weather_response = requests.get(weather_url)
            self.weather_data = weather_response.json()

            # Get forecast data
            forecast_response = requests.get(forecast_url)
            self.forecast_data = forecast_response.json()

            self.update_dashboard()

        except Exception as e:
            messagebox.showerror("Error", f"Error fetching weather data: {str(e)}")

    def update_dashboard(self):
        # Clear previous content
        for widget in self.current_weather_frame.winfo_children():
            widget.destroy()
        for widget in self.forecast_frame.winfo_children():
            widget.destroy()

        # Update current weather
        self.update_current_weather()

        # Update forecast
        self.update_forecast()

    def update_current_weather(self):
        if not self.weather_data:
            return

        # City name and date
        city_name = self.weather_data['name']
        country = self.weather_data['sys']['country']

        header = tk.Label(
            self.current_weather_frame,
            text=f"{city_name}, {country}",
            font=("Helvetica", 20, "bold"),
            bg="white"
        )
        header.pack(pady=10)

        # Current temperature
        temp = self.weather_data['main']['temp']
        temp_label = tk.Label(
            self.current_weather_frame,
            text=f"{temp}°C",
            font=("Helvetica", 36),
            bg="white"
        )
        temp_label.pack()

        # Weather description
        description = self.weather_data['weather'][0]['description'].capitalize()
        desc_label = tk.Label(
            self.current_weather_frame,
            text=description,
            font=("Helvetica", 14),
            bg="white"
        )
        desc_label.pack()

        # Additional weather details
        details_frame = tk.Frame(self.current_weather_frame, bg="white")
        details_frame.pack(fill=tk.X, padx=20, pady=20)

        # Humidity
        humidity = self.weather_data['main']['humidity']
        humidity_label = tk.Label(
            details_frame,
            text=f"Humidity: {humidity}%",
            font=("Helvetica", 12),
            bg="white"
        )
        humidity_label.pack()

        # Wind speed
        wind = self.weather_data['wind']['speed']
        wind_label = tk.Label(
            details_frame,
            text=f"Wind: {wind} m/s",
            font=("Helvetica", 12),
            bg="white"
        )
        wind_label.pack()

        # Pressure
        pressure = self.weather_data['main']['pressure']
        pressure_label = tk.Label(
            details_frame,
            text=f"Pressure: {pressure} hPa",
            font=("Helvetica", 12),
            bg="white"
        )
        pressure_label.pack()

        # Create temperature graph
        self.create_temperature_graph()

    def update_forecast(self):
        if not self.forecast_data:
            return

        # Header
        header = tk.Label(
            self.forecast_frame,
            text="5-Day Forecast",
            font=("Helvetica", 16, "bold"),
            bg="white"
        )
        header.pack(pady=10)

        # Create forecast cards
        for item in self.forecast_data['list'][::8]:  # Get one forecast per day
            date = datetime.fromtimestamp(item['dt']).strftime('%A')
            temp = item['main']['temp']
            description = item['weather'][0]['description'].capitalize()

            # Create card frame
            card = tk.Frame(self.forecast_frame, bg="white", relief=tk.RAISED, bd=1)
            card.pack(fill=tk.X, padx=10, pady=5)

            # Add forecast details
            date_label = tk.Label(card, text=date, font=("Helvetica", 12), bg="white")
            date_label.pack()

            temp_label = tk.Label(card, text=f"{temp}°C", font=("Helvetica", 12, "bold"), bg="white")
            temp_label.pack()

            desc_label = tk.Label(card, text=description, font=("Helvetica", 10), bg="white")
            desc_label.pack()

    def create_temperature_graph(self):
        # Create figure
        fig, ax = plt.subplots(figsize=(5, 3))

        # Get temperature data from forecast
        dates = []
        temps = []

        for item in self.forecast_data['list'][:8]:  # Next 24 hours
            date = datetime.fromtimestamp(item['dt']).strftime('%H:%M')
            temp = item['main']['temp']
            dates.append(date)
            temps.append(temp)

        # Create the line plot
        ax.plot(dates, temps, marker='o')
        ax.set_title("24-Hour Temperature Forecast")
        ax.set_xlabel("Time")
        ax.set_ylabel("Temperature (°C)")
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Embed the plot in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.current_weather_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

    def run(self):
        self.root.mainloop()


# Create and run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDashboard(root)
    app.run()