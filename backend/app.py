import os
import random
from datetime import datetime, date
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv(override=True)

app = Flask(__name__)
CORS(app)

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"


def build_packing_suggestions(forecast_list, units="imperial"):
    suggestions = set()

    if not forecast_list:
        return ["No packing suggestions available yet."]

    max_temp = max(day["temp_max"] for day in forecast_list)
    min_temp = min(day["temp_min"] for day in forecast_list)
    avg_wind = sum(day["wind_speed"] for day in forecast_list) / len(forecast_list)

    rainy_days = sum(
        1 for day in forecast_list
        if "rain" in day["description"].lower() or "drizzle" in day["description"].lower()
    )

    cold_threshold = 55 if units == "imperial" else 13
    hot_threshold = 80 if units == "imperial" else 27

    if min_temp < cold_threshold:
        suggestions.add("Pack a hoodie or light jacket.")
        suggestions.add("Bring long pants.")

    if max_temp > hot_threshold:
        suggestions.add("Pack sunscreen.")
        suggestions.add("Bring sunglasses.")

    if rainy_days > 0:
        suggestions.add("Bring an umbrella.")
        suggestions.add("Pack a raincoat.")

    if avg_wind > (12 if units == "imperial" else 5):
        suggestions.add("Bring a light windbreaker.")

    suggestions.add("Bring comfortable walking shoes.")

    return sorted(suggestions)


def build_city_aware_event_suggestions(city, forecast_list):
    if not forecast_list:
        return ["No suggestions available."]

    normalized = city.strip().lower()

    rainy_days = sum(
        1 for day in forecast_list
        if "rain" in day["description"].lower() or "drizzle" in day["description"].lower()
    )
    hot_days = sum(1 for day in forecast_list if day["temp_max"] >= 85)
    cold_days = sum(1 for day in forecast_list if day["temp_min"] <= 50)

    city_specific = {
        "seattle": {
            "indoor": [
                "Check out the Seattle Art Museum",
                "Grab coffee and explore Pike Place Market",
                "Visit the Museum of Pop Culture"
            ],
            "outdoor": [
                "Walk around Pike Place and the waterfront",
                "Visit the Space Needle area",
                "Explore Kerry Park or other viewpoints"
            ]
        },
        "washington dc": {
            "indoor": [
                "Visit one of the Smithsonian museums",
                "Check out indoor exhibits near the National Mall",
                "Take a museum-heavy day around downtown"
            ],
            "outdoor": [
                "Walk around the National Mall monuments",
                "Visit the Capitol and surrounding landmarks",
                "Explore memorials and photo spots"
            ]
        },
        "washington, dc": {
            "indoor": [
                "Visit one of the Smithsonian museums",
                "Check out indoor exhibits near the National Mall",
                "Take a museum-heavy day around downtown"
            ],
            "outdoor": [
                "Walk around the National Mall monuments",
                "Visit the Capitol and surrounding landmarks",
                "Explore memorials and photo spots"
            ]
        },
        "toronto": {
            "indoor": [
                "Visit the Royal Ontario Museum",
                "Explore indoor spots around downtown",
                "Check out cafes and shopping near the core"
            ],
            "outdoor": [
                "Visit the CN Tower area",
                "Walk along the Toronto waterfront",
                "Explore downtown photo spots"
            ]
        },
        "nassau": {
            "indoor": [
                "Explore Marina Village shops and cafes",
                "Relax at indoor resort spaces around Atlantis",
                "Check out local food spots and covered areas"
            ],
            "outdoor": [
                "Spend time around Atlantis Resort",
                "Visit nearby beaches and waterfront areas",
                "Walk around scenic marina and resort spots"
            ]
        },
        "nassau bahamas": {
            "indoor": [
                "Explore Marina Village shops and cafes",
                "Relax at indoor resort spaces around Atlantis",
                "Check out local food spots and covered areas"
            ],
            "outdoor": [
                "Spend time around Atlantis Resort",
                "Visit nearby beaches and waterfront areas",
                "Walk around scenic marina and resort spots"
            ]
        },
        "new york": {
            "indoor": [
                "Visit a museum like MoMA or the Met",
                "Warm up in cafes and indoor food halls",
                "Catch a Broadway or indoor show"
            ],
            "outdoor": [
                "Walk through Central Park or downtown areas",
                "Visit major skyline and landmark viewpoints",
                "Explore neighborhoods and photo spots"
            ]
        },
        "chicago": {
            "indoor": [
                "Visit the Art Institute of Chicago",
                "Check out indoor attractions on Michigan Avenue",
                "Warm up with local food and cafes"
            ],
            "outdoor": [
                "Walk along the Riverwalk",
                "Visit skyline viewpoints and lakefront areas",
                "Explore Millennium Park"
            ]
        },
        "portland": {
            "indoor": [
                "Visit coffee shops and book stores",
                "Check out indoor food halls or local cafes",
                "Spend time in museums or galleries"
            ],
            "outdoor": [
                "Explore local neighborhoods and parks",
                "Walk the waterfront or downtown",
                "Visit scenic viewpoints if weather is clear"
            ]
        }
    }

    default_indoor = [
        "Visit a museum or local gallery",
        "Check out cafes and coffee shops",
        "Spend time at indoor attractions nearby"
    ]

    default_outdoor = [
        "Explore parks or scenic areas",
        "Walk around local neighborhoods",
        "Visit landmarks and photo spots"
    ]

    city_data = city_specific.get(normalized, {})
    indoor_options = city_data.get("indoor", default_indoor)
    outdoor_options = city_data.get("outdoor", default_outdoor)

    suggestions = []

    if rainy_days > 0:
        suggestions.extend(random.sample(indoor_options, min(2, len(indoor_options))))
    else:
        suggestions.extend(random.sample(outdoor_options, min(2, len(outdoor_options))))

    if hot_days > 0:
        suggestions.append("Plan a lighter outdoor stop and stay hydrated")
    elif cold_days > 0:
        suggestions.append("Mix in a warm indoor stop like a cafe or museum")
    else:
        suggestions.append("Leave time for a relaxed walk around the area")

    unique = list(dict.fromkeys(suggestions))
    return unique[:3]


def get_trip_label(forecast_list):
    if not forecast_list:
        return "Trip outlook"

    rainy_days = sum(
        1 for day in forecast_list
        if "rain" in day["description"].lower() or "drizzle" in day["description"].lower()
    )
    clear_days = sum(
        1 for day in forecast_list
        if "clear" in day["description"].lower()
    )
    avg_temp = sum(day["temp_avg"] for day in forecast_list) / len(forecast_list)

    if rainy_days >= max(1, len(forecast_list) // 2):
        return "Rainy trip"
    if clear_days >= max(1, len(forecast_list) // 2):
        return "Sunny trip"
    if avg_temp <= 58:
        return "Cooler trip"
    return "Mixed weather"


def get_best_days(forecast_list):
    if not forecast_list:
        return {
            "best_outdoor_day": None,
            "best_indoor_day": None
        }

    def outdoor_score(day):
        score = 0
        description = day["description"].lower()

        if "clear" in description:
            score += 4
        if "cloud" in description:
            score += 2
        if "rain" in description or "drizzle" in description:
            score -= 5
        if 60 <= day["temp_avg"] <= 82:
            score += 3
        if day["wind_speed"] <= 12:
            score += 2
        return score

    def indoor_score(day):
        score = 0
        description = day["description"].lower()

        if "rain" in description or "drizzle" in description:
            score += 5
        if day["temp_avg"] < 55 or day["temp_avg"] > 88:
            score += 3
        if day["wind_speed"] > 14:
            score += 2
        return score

    best_outdoor = max(forecast_list, key=outdoor_score)
    best_indoor = max(forecast_list, key=indoor_score)

    return {
        "best_outdoor_day": best_outdoor["date"],
        "best_indoor_day": best_indoor["date"]
    }


def build_summary(city, forecast_list):
    if not forecast_list:
        return f"No forecast summary available for {city}."

    descriptions = [day["condition"] for day in forecast_list]
    most_common = max(set(descriptions), key=descriptions.count)

    avg_temp = sum(day["temp_avg"] for day in forecast_list) / len(forecast_list)
    min_temp = min(day["temp_min"] for day in forecast_list)
    max_temp = max(day["temp_max"] for day in forecast_list)

    return (
        f"Your trip to {city} will be mostly {most_common.lower()}, "
        f"with temperatures from {round(min_temp)}° to {round(max_temp)}°. "
        f"Average around {round(avg_temp)}°."
    )


def summarize_daily_forecast(filtered_entries):
    daily_data = {}

    for item in filtered_entries:
        dt = datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S")
        day_date = str(dt.date())
        time = dt.strftime("%I:%M %p")

        if day_date not in daily_data:
            daily_data[day_date] = {
                "date": day_date,
                "temps": [],
                "temps_min": [],
                "temps_max": [],
                "conditions": [],
                "descriptions": [],
                "humidities": [],
                "winds": [],
                "icon": item["weather"][0]["icon"],
                "time_slots": []
            }

        daily_data[day_date]["temps"].append(item["main"]["temp"])
        daily_data[day_date]["temps_min"].append(item["main"]["temp_min"])
        daily_data[day_date]["temps_max"].append(item["main"]["temp_max"])
        daily_data[day_date]["conditions"].append(item["weather"][0]["main"])
        daily_data[day_date]["descriptions"].append(item["weather"][0]["description"])
        daily_data[day_date]["humidities"].append(item["main"]["humidity"])
        daily_data[day_date]["winds"].append(item["wind"]["speed"])

        daily_data[day_date]["time_slots"].append({
            "time": time,
            "condition": item["weather"][0]["main"],
            "description": item["weather"][0]["description"],
            "temp": round(item["main"]["temp"], 1),
            "temp_min": round(item["main"]["temp_min"], 1),
            "temp_max": round(item["main"]["temp_max"], 1),
            "humidity": item["main"]["humidity"],
            "wind_speed": item["wind"]["speed"],
            "icon": item["weather"][0]["icon"]
        })

    result = []

    for day_date, values in daily_data.items():
        condition = max(set(values["conditions"]), key=values["conditions"].count)
        description = max(set(values["descriptions"]), key=values["descriptions"].count)

        result.append({
            "date": day_date,
            "condition": condition,
            "description": description,
            "temp_min": round(min(values["temps_min"]), 1),
            "temp_max": round(max(values["temps_max"]), 1),
            "temp_avg": round(sum(values["temps"]) / len(values["temps"]), 1),
            "humidity": round(sum(values["humidities"]) / len(values["humidities"])),
            "wind_speed": round(sum(values["winds"]) / len(values["winds"]), 1),
            "icon": values["icon"],
            "time_slots": values["time_slots"]
        })

    return sorted(result, key=lambda x: x["date"])


@app.route("/api/trip-weather")
def trip_weather():
    city = request.args.get("city")
    start = request.args.get("start")
    end = request.args.get("end")
    units = request.args.get("units", "imperial")

    if not city or not start or not end:
        return jsonify({"error": "City and trip dates are required."}), 400

    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    today = date.today()

    if start_date < today or end_date < today:
        return jsonify({"error": "Please choose today or a future date."}), 400

    if end_date < start_date:
        return jsonify({"error": "End date cannot be earlier than start date."}), 400

    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": units
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        res = response.json()
    except requests.HTTPError:
        return jsonify({
            "error": "City not found. Try another destination or check the spelling."
        }), 404
    except requests.RequestException:
        return jsonify({
            "error": "Weather service unavailable right now. Try again in a moment."
        }), 500

    filtered = [
        item for item in res["list"]
        if start_date <= datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S").date() <= end_date
    ]

    if not filtered:
        return jsonify({
            "error": "This planner currently supports trips in the next 5 days because of the weather API forecast limit."
        }), 400

    daily = summarize_daily_forecast(filtered)
    best_days = get_best_days(daily)

    return jsonify({
        "destination": city,
        "forecast": daily,
        "packing_suggestions": build_packing_suggestions(daily, units),
        "event_suggestions": build_city_aware_event_suggestions(city, daily),
        "summary": build_summary(city, daily),
        "trip_label": get_trip_label(daily),
        "best_outdoor_day": best_days["best_outdoor_day"],
        "best_indoor_day": best_days["best_indoor_day"],
        "units": units
    })


if __name__ == "__main__":
    app.run(debug=True)