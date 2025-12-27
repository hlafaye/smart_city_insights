# Smart City Insight 🌍

Smart City Insight is a web application that evaluates city livability using
real-time data from traffic, weather, and air quality APIs.

## Features
- Smart city search (TomTom geocoding)
- Weather snapshot (OpenWeather)
- Air quality index (AQI + pollutants)
- Traffic index (multi-point sampling)
- Composite score (0–100) with reliability weighting

## Tech stack
- Python / Flask
- Jinja2 / Bootstrap 5
- JavaScript
- Docker


## Create a .env file
- APP_KEY= Flask app custom key
- OSM_KEY= Open weather map API key
- GPS_KEY= TomTom API key

## Built to be deployed with docker
Docker deploy ready.

## Local setup

```bash
git clone ...
cd smart_city_insights
python -m venv .venv
pip install -r requirements.txt

⚠️ Note: This demo runs on a free Render instance.
The first load may take a few seconds and require a refresh due to cold start.

