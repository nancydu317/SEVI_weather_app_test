import pygame  # pygame library for graphics
import requests  # library to extract APIs
import json  # library to read JSON files
import os  # library to extract file directory
from datetime import *

import pygame_textinput  # add file to app folder

# define some colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# define Earth weather text display variables:
weather_var = {
    "show_location": "",
    "show_current_temp": "",
    "show_current_temp_units": "",
    "show_forecast": "",
    "show_update_time": "",
    "show_date": "",
    "show_high": "",
    "show_low": "",
    "show_sunrise_time": "",
    "show_sunset_time": "",
    "show_uvi": "",
    "show_pressure": "",
    "show_humidity": "",
    "show_windspeed": "",
    "show_cloud_bh": "",
    "show_cloud_type": ""
}

# graphics variables
background = ""
backgroundRect = ""
font_col = ""

# convert from epoch to standard time
def convert_time(time):
    standard_time = datetime.fromtimestamp(time)
    return standard_time

# =============================== API Data ======================================
# API URLs
API_KEY = "bc93af7ec21317a25fa7d755f7391e39"
geo_URL = "http://api.openweathermap.org/geo/1.0/direct?"
weather_URL = "https://api.openweathermap.org/data/2.5/onecall?"
city_name = ""
lat = ""
lon = ""

def getLocation():
    global city_name, lat, lon, new_city_click
    city_name = "Toronto"  # start off with a local city
    if new_city_click == True:
        city_name = textinput.get_text()
        new_city_click = False

    # Extract Coordinates using Geocoding API
    geo_parameters = {
        "q": city_name,
        "appid": API_KEY
    }
    geo_response = requests.get(geo_URL, params=geo_parameters)
    print("Geocode API Status:", geo_response.status_code)
    geo_coord = geo_response.json()
    geo_first = geo_coord[0]  # get first item in list of possible cities (most popular)
    lat = float(geo_first["lat"])  # north is positive, south is negative
    lon = float(geo_first["lon"])  # east is positive, west is negative

# determine cloud type
def cloud_base_height(temp, dew):
    cloud_base = (temp - dew) / 2.5 * 1000 / 3.280839895
    print("The height of clouds is", round(cloud_base), "metres")
    return cloud_base

def getWeather():
    global city_name, lat, lon
    global background, backgroundRect, font_col
    global weather_var

    update_time = datetime.now()  # get the current time
    weather_var['show_update_time'] = (f"{update_time.strftime('%I')}:" + f"{update_time.strftime('%M')}" + f" {update_time.strftime('%p')}")

    # Extract City Weather using One Call Weather API
    weather_parameters = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric"
    }

    weather_response = requests.get(weather_URL, params=weather_parameters)
    print("One Call Weather API Status:", weather_response.status_code)
    weather_data = weather_response.json()
    current_weather = weather_data["current"]
    daily_weather = (weather_data["daily"])[0]["temp"]

    current_temp = round(current_weather["temp"])  # current temperature
    current_forecast = (current_weather["weather"])[0]["main"]  # current weather forecast
    pressure = current_weather["pressure"]  # current atmospheric pressure in hectopascals (hPa) which equals millibar (mb)
    dew_point = current_weather["dew_point"]  # current dew point temperature
    UVI = current_weather["uvi"]
    wind_speed = round((current_weather["wind_speed"]) * 3.6)  # current wind speed m/s, (x 3.6) to convert to km/h
    humidity = current_weather["humidity"]  # current humidity in %
    date = convert_time(current_weather["dt"])
    sunrise_time = convert_time(current_weather["sunrise"])
    sunset_time = convert_time(current_weather["sunset"])

    # format datetimes, .stftime() is a method to format the datetime object
    weather_var['show_date'] = date.strftime('%x')
    weather_var['show_sunrise_time'] = (
            f"{sunrise_time.strftime('%I')}:" + f"{sunrise_time.strftime('%M')}" + f" {sunrise_time.strftime('%p')}")
    weather_var['show_sunset_time'] = (
            f"{sunset_time.strftime('%I')}:" + f"{sunset_time.strftime('%M')}" + f" {sunset_time.strftime('%p')}")

    daily_max_temp = round(daily_weather["max"], 1)  # daily temperature high
    daily_min_temp = round(daily_weather["min"], 1)  # daily temperature low

    # text to display on app screen
    weather_var['show_forecast'] = str(current_forecast)
    weather_var['show_current_temp'] = str(current_temp)
    weather_var['show_current_temp_units'] = chr(176) + "C"
    weather_var['show_location'] = city_name
    weather_var['show_high'] = f"High: {daily_max_temp}" + chr(176)
    weather_var['show_low'] = f"Low: {daily_min_temp}" + chr(176)

    # text under Show More
    weather_var['show_uvi'] = str(UVI)
    weather_var['show_humidity'] = str(humidity) + " %"
    weather_var['show_pressure'] = str(pressure) + " hPa"

    cloud_type = ""
    cloud_bh = "- -"
    if current_forecast != "Clear":
        cloud_bh = round(cloud_base_height(current_temp, dew_point))
        if cloud_bh < 2000 and current_forecast == "Rain":
            cloud_type = "cumulus"
        elif cloud_bh < 2000:
            cloud_type = "stratus"
        elif 2000 <= cloud_bh < 7000:
            cloud_type = "alto"
        elif cloud_bh >= 7000:
            cloud_type = "cirrus"
    else:
        cloud_type = "None"

    print("The cloud type is", cloud_type)

    weather_var['show_windspeed'] = str(wind_speed) + " km/h"
    weather_var['show_cloud_bh'] = str(cloud_bh) + " m"
    weather_var['show_cloud_type'] = cloud_type

    # Background Weather Image
    if current_forecast == "Thunderstorm" or current_forecast == "Drizzle" or current_forecast == "Rain":
        weather_bkgd = "bkgd_rain.png"
        font_col = WHITE
    elif current_forecast == "Snow":
        weather_bkgd = "bkgd_snow.png"
        font_col = BLACK
    elif current_forecast == "Clear":
        weather_bkgd = "bkgd_clear.png"
        font_col = BLACK
    elif current_forecast == "Clouds":
        weather_bkgd = "bkgd_clouds.png"
        font_col = BLACK
    else:
        weather_bkgd = "bkgd_clouds.png"
        font_col = BLACK

    background_file = os.path.join(img_folder, weather_bkgd)
    background = pygame.image.load(background_file)
    backgroundRect = background.get_rect()

# ======================== GRAPHICS ==========================
# screen setup
WIDTH = 800
HEIGHT = 600
FPS = 30

# initialize pygame
pygame.init()

# create window and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Earth Weather App")
clock = pygame.time.Clock()

# create file paths
app_folder = os.path.dirname(__file__)  # gets the path of the current file
img_folder = os.path.join(app_folder, "images")  # the join functions lets you add an image to it
app_icon_file = os.path.join(img_folder, "weather_icon_test4.png")

# Button file paths
refresh_button_file = os.path.join(img_folder, "refresh_button.png")
search_button_file = os.path.join(img_folder, "search_location_button.png")
show_more_button_file = os.path.join(img_folder, "show_more_button.png")
hide_button_file = os.path.join(img_folder, "hide_button.png")

# load background images to pygame
# everytime we add an image, need the get_rect to be able to set position dimensions on screen
app_icon = pygame.image.load(app_icon_file)
pygame.display.set_icon(app_icon)

# create button Rects
search_button = pygame.image.load(search_button_file)
search_buttonRect = search_button.get_rect(topleft=(360,10))
refresh_button = pygame.image.load(refresh_button_file)
refresh_buttonRect = refresh_button.get_rect(topleft=(500,10))
show_more_button = pygame.image.load(show_more_button_file)
show_more_buttonRect = show_more_button.get_rect(topleft=(600, 125))
hide_button = pygame.image.load(hide_button_file)
hide_buttonRect = hide_button.get_rect(topleft=(565,130))

# function to display text on screen
def display_text(size, text, colour, x, y):
    font = pygame.font.Font('freesansbold.ttf', size)  # specify the font and size
    textSurf = font.render(text, True, colour)    # create a surface for the text object
    textRect = textSurf.get_rect()  # get rect position of text on the screen
    textRect.topleft = (x, y)  # specify rect position of text on screen
    screen.blit(textSurf, textRect)  # show the text on the screen

# display text input box
textinput = pygame_textinput.TextInput(initial_string="Toronto", font_size=30)

def showMore():
    global weather_var
    # Icon file paths
    sunrise_icon_file = os.path.join(img_folder, "sunrise_icon.png")
    sunset_icon_file = os.path.join(img_folder, "sunset_icon.png")
    UVI_icon_file = os.path.join(img_folder, "UVI_icon.png")
    pressure_icon_file = os.path.join(img_folder, "pressure_icon.png")
    humidity_icon_file = os.path.join(img_folder, "humidity_icon.png")

    # create icon rects
    icon_x = 565
    icon_y = 180
    sunrise_i = pygame.image.load(sunrise_icon_file)
    sunrise_iRect = sunrise_i.get_rect(topleft=(icon_x, icon_y))
    icon_h = sunrise_iRect.height

    sunset_i = pygame.image.load(sunset_icon_file)
    sunset_iRect = sunset_i.get_rect(topleft=(icon_x, icon_y + icon_h + 10))
    UVI_i = pygame.image.load(UVI_icon_file)
    UVI_iRect = UVI_i.get_rect(topleft=(icon_x, icon_y + 2 * (icon_h + 10)))
    pressure_i = pygame.image.load(pressure_icon_file)
    pressure_iRect = pressure_i.get_rect(topleft=(icon_x, icon_y + 3 * (icon_h + 10)))
    humidity_i = pygame.image.load(humidity_icon_file)
    humidity_iRect = humidity_i.get_rect(topleft=(icon_x, icon_y + 4 * (icon_h + 10)))

    # draw weather info text
    display_text(16, f"Sunrise: {weather_var['show_sunrise_time']}", font_col, 600, sunrise_iRect.top + 5)
    display_text(16, f"Sunset: {weather_var['show_sunset_time']}", font_col, 600, sunset_iRect.top + 5)
    display_text(16, f"UV Index: {weather_var['show_uvi']}", font_col, 600, UVI_iRect.top + 5)
    display_text(16, f"Pressure: {weather_var['show_pressure']}", font_col, 600, pressure_iRect.top + 5)
    display_text(16, f"Humidity: {weather_var['show_humidity']}", font_col, 600, humidity_iRect.top + 5)

    # draw weather MORE info icons on screen
    screen.blit(sunrise_i, sunrise_iRect)
    screen.blit(sunset_i, sunset_iRect)
    screen.blit(UVI_i, UVI_iRect)
    screen.blit(pressure_i, pressure_iRect)
    screen.blit(humidity_i, humidity_iRect)

# App Conditions
running = True  # this means that app will run while this variable is true
show_more_click = False
new_city_click = False

# get location and weather data when app launches
getLocation()
getWeather()  # Initialize weather data

# ====================== APP DISPLAY LOOP =========================
while running:
    # regulate the speed
    clock.tick(FPS)

    # process user input
    events = pygame.event.get()
    for event in events:
        mouse = pygame.mouse.get_pos()  # get mouse position (x, y)

        if event.type == pygame.QUIT:
            running = False  # stop game and quite

        if event.type == pygame.MOUSEBUTTONDOWN:
            print("Mouse click!")
            if pygame.Rect.collidepoint(refresh_buttonRect, mouse):  # if refresh button overlaps with mouse position
                print("REFRESH!")
                getWeather()
            elif pygame.Rect.collidepoint(search_buttonRect, mouse): # if new city button overlaps with mouse position
                print("NEW CITY")
                new_city_click = True
                getLocation()
                getWeather()
            elif pygame.Rect.collidepoint(show_more_buttonRect, mouse): # if more button overlaps with mouse position
                print("SHOW MORE!!!")
                show_more_click = True
            elif pygame.Rect.collidepoint(hide_buttonRect, mouse):
                print("HIDE MENU")
                show_more_click = False

    # render/draw the screen
    screen.fill(BLACK)
    screen.blit(background, backgroundRect)

    # draw buttons
    screen.blit(refresh_button, refresh_buttonRect)
    screen.blit(search_button, search_buttonRect)
    screen.blit(show_more_button, show_more_buttonRect)

    # display_text(size, text, colour, x, y)
    # display_text(25, weather_var['show_location'], font_col, 70, 20)
    display_text(150, weather_var['show_current_temp'], font_col, 40, 55)
    display_text(40, weather_var['show_current_temp_units'], font_col, 205, 65)
    display_text(25, weather_var['show_forecast'], font_col, 45, 200)
    display_text(20, f"Last Updated: {weather_var['show_update_time']}", font_col, 550, 20)
    display_text(60, weather_var['show_date'], font_col, 550, 55)
    display_text(20, weather_var['show_high'], font_col, 80, 400)
    display_text(20, weather_var['show_low'], font_col, 80, 460)
    # bottom bar text
    display_text(16, weather_var['show_windspeed'], BLACK, 70, 555)
    display_text(16, weather_var['show_cloud_bh'], BLACK, 205, 555)
    display_text(16, weather_var['show_cloud_type'], BLACK, 377, 555)

    # show text input box on screen
    textinput.update(events)
    screen.blit(textinput.get_surface(), (25, 20))

    if show_more_click == True:
        showMore()
        screen.blit(hide_button, hide_buttonRect)

    # display all objects on the screen
    pygame.display.flip()

pygame.quit()
