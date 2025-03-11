import tkinter as tk
from tkinter import ttk, Canvas
from ttkthemes import ThemedTk
import time
import requests
import RPi.GPIO as GPIO
from datetime import datetime
import random
import os
import json

# Load configuration from a separate file (config.json)
CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"API_KEY": "", "CITY": ""}  # Default empty values

config = load_config()

# GPIO Setup for PWM
PWM_PIN_1 = 18  # First light
PWM_PIN_2 = 19  # Second light
GPIO.setmode(GPIO.BCM)
GPIO.setup(PWM_PIN_1, GPIO.OUT)
GPIO.setup(PWM_PIN_2, GPIO.OUT)
pwm1 = GPIO.PWM(PWM_PIN_1, 10000)  
pwm2 = GPIO.PWM(PWM_PIN_2, 100)
pwm1.start(69)  
pwm2.start(0)

# Function to exit the application
def exit_app():
    pwm1.stop()
    pwm2.stop()
    GPIO.cleanup()
    root.destroy()

# Function to toggle fullscreen
def toggle_fullscreen():
    root.attributes("-fullscreen", not root.attributes("-fullscreen"))

# Function to get weather data
def get_weather():
    API_KEY = config.get("API_KEY", "")
    CITY = config.get("CITY", "")
    if not API_KEY or not CITY:
        return "Weather data not configured"
    
    try:
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
        response = requests.get(weather_url)
        weather_data = response.json()

        if weather_data["cod"] == 200:
            temperature = int(weather_data["main"]["temp"])
            weather_description = weather_data["weather"][0]["description"].capitalize()
            return f"{temperature}C, {weather_description}"
        else:
            return "Weather data not available"
    except:
        return "No connection"

# Function to get CPU temperature
def get_cpu_temp():
    try:
        temp = os.popen("vcgencmd measure_temp").readline()
        return temp.replace("temp=", "CPU: ").replace("'C\n", "C")
    except:
        return "CPU Temp N/A"

# Function to update time, weather, and CPU temp
def update_time_weather():
    current_time = datetime.now().strftime('%H:%M:%S')
    time_label.config(text=current_time)
    weather_label.config(text=get_weather())
    cpu_label.config(text=get_cpu_temp())
    root.after(1000, update_time_weather)

# Light toggle function
lights_on = False
def toggle_lights():
    global lights_on
    lights_on = not lights_on
    pwm1.ChangeDutyCycle(100 if lights_on else 0)
    pwm2.ChangeDutyCycle(100 if lights_on else 0)
    light_toggle_button.config(text="Lights OFF" if lights_on else "Lights ON")

# Function to update PWM duty cycle
def update_pwm1(value):
    pwm1.ChangeDutyCycle(float(value))

def update_pwm2(value):
    pwm2.ChangeDutyCycle(float(value))

# Function to animate stars
def update_stars():
    canvas.delete("star")
    for star in stars:
        star[1] += 1  # Move star downward
        if star[1] > 400:
            star[1] = 0  # Reset to top
        x, y, size = star
        canvas.create_oval(x, y, x+size, y+size, fill="white", outline="", tags="star")
    root.after(50, update_stars)

# Create main window
root = ThemedTk(theme="equilux")  # Dark theme
root.title("Dark Mode Clock & PWM Control")
root.geometry("1280x400")
root.attributes("-fullscreen", True)
root.config(cursor="none")  # Hide mouse cursor

# Background Canvas
gradient_bg = Canvas(root, width=1280, height=400, bg="black", highlightthickness=0)
gradient_bg.place(x=0, y=0, relwidth=1, relheight=1)
canvas = Canvas(root, width=1280, height=400, bg="black", highlightthickness=0)
canvas.place(x=0, y=0, relwidth=1, relheight=1)

# Initialize stars
stars = [[random.randint(0, 1280), random.randint(0, 400), random.randint(1, 3)] for _ in range(100)]

# Left Section: Time & Weather
left_frame = ttk.Frame(root, width=850, height=400, style="Dark.TFrame")
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

time_label = ttk.Label(left_frame, font=("Helvetica", 120, "bold"), background="black", foreground="white")
time_label.pack(pady=10)

weather_label = ttk.Label(left_frame, font=("Helvetica", 24), background="black", foreground="#AAAAAA")
weather_label.pack(pady=5)

cpu_label = ttk.Label(left_frame, font=("Helvetica", 20), background="black", foreground="#888888")
cpu_label.pack(pady=5)

# Right Section: PWM Controls & Buttons
right_frame = ttk.Frame(root, width=430, height=400, style="Dark.TFrame")
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

# Light Toggle Button
light_toggle_button = ttk.Button(right_frame, text="Lights ON", command=toggle_lights)
light_toggle_button.pack(pady=10)

slider1 = ttk.Scale(right_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=update_pwm1)
slider1.pack(fill=tk.X, padx=20, pady=5)

slider2 = ttk.Scale(right_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=update_pwm2)
slider2.pack(fill=tk.X, padx=20, pady=5)

fullscreen_button = ttk.Button(right_frame, text="Fullscreen", command=toggle_fullscreen)
fullscreen_button.pack(pady=10)
exit_button = ttk.Button(right_frame, text="Exit", command=exit_app)
exit_button.pack(pady=10)

# Apply styles
style = ttk.Style()
style.configure("Dark.TFrame", background="black")
style.configure("TLabel", background="black", foreground="white")
style.configure("TButton", background="#444444", foreground="white")

# Start animations and updates
update_time_weather()
update_stars()
root.mainloop()
