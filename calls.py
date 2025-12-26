import os 
from dotenv import load_dotenv
import requests as req
from numpy import median, mean
from math import cos, radians

load_dotenv()
OSM_KEY = os.environ.get("OSM_KEY")

def get_infos(lat, lon, bbox):
    
    geocode_params = {
        "lat":lat,
        "lon" : lon,
        "limit": "1",
        "appid": OSM_KEY,}

    geocode_url = "http://api.openweathermap.org/geo/1.0/reverse"
    rep = req.get(url=geocode_url, params=geocode_params, timeout=30)
    rep.raise_for_status()
    data = rep.json()
    name = data[0]['name']
    iso = data[0]['country']
    
    weather = get_weather(lat=lat, lon=lon)
    air = get_air_infos(lat=lat, lon=lon)
    mobility = get_trafic_infos(lat=lat, lon=lon, bbox=bbox)
    
    return name, iso, weather, air, mobility




def get_weather(lat, lon):
    weather_dict = {}
    weather_parameters={
            "lat": lat,
            "lon": lon,
            "lang":"en",
            "units":"metric",
            "cnt":4,
            "appid": OSM_KEY,
        }

    mode={
        "current":"https://api.openweathermap.org/data/2.5/weather",
        "forecast5":"https://api.openweathermap.org/data/2.5/forecast"
    }


    rep = req.get(url= mode["current"], params=weather_parameters, timeout=30)
    rep.raise_for_status()
    weather_data= rep.json()
    weather_dict['temp']=weather_data['main']['temp']
    weather_dict['feels_like']=weather_data['main']['feels_like']
    weather_dict['desc'] = weather_data['weather'][0]['description']
    weather_dict['icon'] =weather_data['weather'][0]['icon'] 
    weather_dict['wind']=weather_data['wind']['speed']
    weather_dict['humidity']=weather_data['main']['humidity']
    return weather_dict


def get_air_infos(lat, lon):
    AQI_META = {
  1: {"label":"Good",      "class":"aqi-1"},
  2: {"label":"Fair",      "class":"aqi-2"},
  3: {"label":"Moderate",  "class":"aqi-3"},
  4: {"label":"Poor",      "class":"aqi-4"},
  5: {"label":"Very Poor", "class":"aqi-5"},
}


    air_dict={}
    air_params = {
        "lat": lat,
        "lon": lon,
        "appid": OSM_KEY,}

    air_url = "http://api.openweathermap.org/data/2.5/air_pollution"
    rep = req.get(url=air_url, params=air_params, timeout=30)
    rep.raise_for_status()
    data = rep.json()
    
    main = data["list"][0]["main"]
    comp = data["list"][0]["components"]

    aqi = main["aqi"]                      
    meta = AQI_META.get(aqi, {"label":"Unknown", "class":"aqi-0"})

    air_dict = {
        "aqi": aqi,
        "label": meta["label"],
        "class": meta["class"],
        "pm2_5": comp["pm2_5"],
        "pm10": comp["pm10"],
        "no2": comp["no2"],
        "o3": comp["o3"],
    }

    return air_dict


def get_trafic_infos(lat, lon, bbox):
    lat_min = bbox["btmRightPoint"]["lat"]
    lat_max = bbox["topLeftPoint"]["lat"]
    lon_min = bbox["topLeftPoint"]["lon"]
    lon_max = bbox["btmRightPoint"]["lon"]

    dlat = lat_max - lat_min
    dlon = lon_max - lon_min

    f1 = 0.25
    f2 = 0.50

    off_lat_1 = dlat * f1
    off_lon_1 = dlon * f1
    off_lat_2 = dlat * f2
    off_lon_2 = dlon * f2

    cos_lat = max(0.2, cos(radians(lat)))

    off_lon_1_corrected = off_lon_1 / cos_lat
    off_lon_2_corrected = off_lon_2 / cos_lat

    OFFSETS = [
    (0, 0),
    (+off_lat_1, 0),
    (-off_lat_1, 0),
    (0, +off_lon_1_corrected),
    (0, -off_lon_1_corrected),
    (+off_lat_2, +off_lon_2_corrected),
    (+off_lat_2, -off_lon_2_corrected),
    (-off_lat_2, +off_lon_2_corrected),
    (-off_lat_2, -off_lon_2_corrected),
]

    TRAFFIC_LEVELS = [
        (0.15, {"label":"Fluid" , "class":"traffic-1"}),
        (0.35, {"label":"Moderate","class":"traffic-2"}),
        (0.60, {"label":"Heavy", "class":"traffic-3" }),
        (1.00, {"label":"Jam", "class":"traffic-4" }),
        ]
    
    DATA_RELIABILITY = [
        (0.20, {"label": "Poor",   "class": "q-1"}),
        (0.40, {"label": "Low",    "class": "q-2"}),
        (0.75, {"label": "Medium", "class": "q-3"}),
        (1.0, {"label": "High",   "class": "q-4"}),
        ]



    trafic_url = "https://api.tomtom.com/traffic/services/4/flowSegmentData/relative0/10/json"

    samples = {}
    for i, offset in enumerate(OFFSETS):   
        latoff, lonoff = offset
        trafic_params={
            "point": f"{lat+latoff},{lon+lonoff}",
            "unit": "KMPH",
            "key": os.environ.get('GPS_KEY')
        }

        try: 
            rep = req.get(url=trafic_url, params=trafic_params, timeout=30)
            rep.raise_for_status()
        except req.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else None
            if status == 400:
                continue  
            continue     
        except req.exceptions.RequestException:
            continue

        data = rep.json()
        currentSpeed = data['flowSegmentData']['currentSpeed']
        freeFlowSpeed = data['flowSegmentData']['freeFlowSpeed']
        confidence = data['flowSegmentData']['confidence']
        ratio = currentSpeed / max(freeFlowSpeed, 1)
        congestion = 1 - ratio

        samples[i] = {
            "ratio": ratio,
            "congestion": congestion,
            "confidence": confidence,
        }
   
    cong_eff = []
    conf_val =[]
    for s in samples.values():

        if s['confidence'] < 0.3:
            continue

        congestion_effective = s['congestion'] * s['confidence']
        cong_eff.append(congestion_effective)
        conf_val.append(s['confidence'])
    
    if not cong_eff:
        return {
            "index": None,
            "label": "No data",
            "class": "muted",
            "quality": 0,
            "quality_label": "No coverage",
            "quality_class": "muted",
        }

    N_total = len(OFFSETS)
    N_ok = len(samples)          
    N_used = len(cong_eff)       

    coverage_attempt = N_ok / max(N_total, 1)
    coverage_used = N_used / max(N_ok, 1)


    trafic_index = median(cong_eff)
    # coverage = len(cong_eff)/len(OFFSETS)
    data_quality = min(1.0, mean(conf_val) * coverage_attempt * coverage_used)



    meta = pick_level(trafic_index ,TRAFFIC_LEVELS)
    reliability = pick_level(data_quality, DATA_RELIABILITY)
  

    return {
        "index": trafic_index,
        "label": meta["label"],
        "class": meta["class"],
        "quality": round(data_quality, 2),
        "quality_label": reliability["label"],
        "quality_class": reliability["class"],
        }



def pick_level(value, levels, default=None):
    for max_v, meta in levels:
        if value <= max_v:
            return meta
    return default or {"label": "Unknown", "class": "traffic-0"}


def search(entry):
    print(entry)
    search_params={
            "key": os.environ.get('GPS_KEY'),
            "language": "en-US",
            "typehead": "true",
            "limit" : "5",
            "idxSet":"Geo",

        }
    
    search_url=f"https://api.tomtom.com/search/2/search/{entry}.json"
    rep = req.get(url=search_url, params=search_params, timeout=30)
    rep.raise_for_status()
    data = rep.json()
    results = []
    
    results = []

    for result in data.get("results", []):
        if result.get("type") != "Geography":
            continue

        addr = result.get("address", {})

        name = (
            addr.get("municipality")
            or addr.get("municipalitySubdivision")
            or addr.get("freeformAddress")
        )

        results.append({
            "name": name,
            "iso": addr.get("countryCode"),
            "lat": result.get("position", {}).get("lat"),
            "lon": result.get("position", {}).get("lon"),
            "bbox": result.get("boundingBox"),
        })

        seen = set()
        clean = []
        for r in results:
            key = (r["name"], r["iso"])
            if key in seen:
                continue
            seen.add(key)
            clean.append(r)

    return clean

       








