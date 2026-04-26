import os
from datetime import datetime, date
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv(override=True)

app = Flask(__name__)
CORS(app)

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"
GEOAPIFY_GEOCODE_URL = "https://api.geoapify.com/v1/geocode/search"
GEOAPIFY_PLACES_URL = "https://api.geoapify.com/v2/places"


@app.route("/")
def home():
    return "Trip Weather Planner API is running."


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


def get_city_coordinates(city):
    if not GEOAPIFY_API_KEY:
        print("GEOAPIFY DEBUG: Missing GEOAPIFY_API_KEY")
        return None

    city_clean = city.strip().lower()

    city_aliases = {
        "toronto": "Toronto, Ontario, Canada",
        "toronto canada": "Toronto, Ontario, Canada",
        "toronto ontario": "Toronto, Ontario, Canada",
        "nassau": "Nassau, New Providence, Bahamas",
        "nassau bahamas": "Nassau, New Providence, Bahamas",
        "nassau, bahamas": "Nassau, New Providence, Bahamas",
        "mexico": "Mexico City, Mexico",
        "mexico city": "Mexico City, Mexico",
        "alaska": "Anchorage, Alaska, United States",
        "anchorage": "Anchorage, Alaska, United States",
        "anchorage alaska": "Anchorage, Alaska, United States",
        "anchorage, alaska": "Anchorage, Alaska, United States",
        "washington dc": "Washington, DC, United States",
        "washington, dc": "Washington, DC, United States",
        "dc": "Washington, DC, United States",
        "salem": "Salem, Oregon, United States",
        "salem oregon": "Salem, Oregon, United States",
        "salem, oregon": "Salem, Oregon, United States",
        "portland": "Portland, Oregon, United States",
        "portland oregon": "Portland, Oregon, United States",
        "portland, oregon": "Portland, Oregon, United States",
    }

    search_text = city_aliases.get(city_clean, city)

    params = {
        "text": search_text,
        "format": "json",
        "limit": 1,
        "type": "city",
        "apiKey": GEOAPIFY_API_KEY,
    }

    try:
        response = requests.get(GEOAPIFY_GEOCODE_URL, params=params, timeout=10)
        print("GEOAPIFY GEOCODE STATUS:", response.status_code)
        print("GEOAPIFY GEOCODE URL:", response.url)

        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        print("GEOAPIFY GEOCODE RESULT COUNT:", len(results))

        if not results:
            print("GEOAPIFY DEBUG: No geocode result found.")
            return None

        coords = {
            "lat": results[0]["lat"],
            "lon": results[0]["lon"],
        }

        print("GEOAPIFY COORDS:", coords)
        return coords

    except requests.RequestException as e:
        print("GEOAPIFY GEOCODE ERROR:", e)
        return None


def choose_place_categories(forecast_list, units="imperial"):
    if not forecast_list:
        return [
            "tourism.attraction",
            "tourism.attraction.viewpoint",
            "tourism.sights",
            "leisure.park",
            "entertainment.museum",
        ]

    rainy_days = sum(
        1 for day in forecast_list
        if "rain" in day["description"].lower() or "drizzle" in day["description"].lower()
    )

    avg_temp = sum(day["temp_avg"] for day in forecast_list) / len(forecast_list)

    hot_threshold = 82 if units == "imperial" else 28
    cold_threshold = 55 if units == "imperial" else 13

    if rainy_days > 0 or avg_temp <= cold_threshold:
        return [
            "entertainment.museum",
            "entertainment.culture.gallery",
            "entertainment.aquarium",
            "entertainment.cinema",
            "commercial.shopping_mall",
            "tourism.sights",
            "tourism.attraction",
        ]

    if avg_temp >= hot_threshold:
        return [
            "beach",
            "leisure.park",
            "tourism.attraction",
            "tourism.attraction.viewpoint",
            "entertainment.aquarium",
            "tourism.sights",
        ]

    return [
        "tourism.attraction",
        "tourism.attraction.viewpoint",
        "tourism.sights",
        "leisure.park",
        "entertainment.museum",
        "entertainment.culture.gallery",
    ]


def clean_category(category):
    parts = category.split(".")
    clean = parts[-1]
    return clean.replace("_", " ").title()


def clean_category_list(categories):
    skip_labels = {
        "Tourism",
        "Entertainment",
        "Building",
        "Commercial",
        "Catering",
        "No Fee",
        "No",
        "Wheelchair",
        "Yes",
        "Limited",
        "Access",
        "Named",
        "Details",
        "Contact",
        "Facilities",
        "Internet Access",
        "Fee",
    }

    priority_labels = [
        "Museum",
        "Aquarium",
        "Beach",
        "Park",
        "Viewpoint",
        "Landmark",
        "Monument",
        "Memorial",
        "Attraction",
        "Cinema",
        "Shopping Mall",
        "Cafe",
        "Restaurant",
    ]

    cleaned = []

    for category in categories:
        clean = clean_category(category)

        if clean in skip_labels:
            continue

        if clean == "Artwork":
            clean = "Statue"

        if clean == "Sights":
            clean = "Landmark"

        if clean == "Gallery":
            continue

        if clean not in cleaned:
            cleaned.append(clean)

    for label in priority_labels:
        if label in cleaned:
            return [label]

    return cleaned[:1]


def is_famous_landmark(name, city):
    if not name:
        return False

    name_lower = name.lower()
    city_lower = city.lower()

    famous_by_city = {
        "seattle": [
            "space needle",
            "pike place",
            "kerry park",
            "seattle center",
            "seattle art museum",
            "waterfront",
        ],
        "toronto": [
            "cn tower",
            "royal ontario museum",
            "harbourfront",
            "casa loma",
            "ripley's aquarium",
        ],
        "nassau": [
            "atlantis",
            "paradise island",
            "queen's staircase",
            "parliament square",
            "rawson square",
            "fort charlotte",
            "junkanoo beach",
        ],
        "nassau bahamas": [
            "atlantis",
            "paradise island",
            "queen's staircase",
            "parliament square",
            "rawson square",
            "fort charlotte",
            "junkanoo beach",
        ],
        "orlando": [
            "lake eola",
            "icon park",
            "orlando museum of art",
            "disney",
            "universal",
        ],
        "washington dc": [
            "smithsonian",
            "lincoln memorial",
            "national mall",
            "capitol",
            "white house",
            "washington monument",
        ],
        "salem": [
            "oregon state capitol",
            "riverfront park",
            "willamette heritage center",
        ],
    }

    for city_key, landmarks in famous_by_city.items():
        if city_key in city_lower:
            return any(landmark in name_lower for landmark in landmarks)

    return False


def get_place_type(name, categories):
    category_text = " ".join(categories).lower()
    name_lower = name.lower()

    if "artwork" in category_text or "statue" in category_text:
        return "statue"

    if "museum" in category_text:
        return "museum"

    if "gallery" in category_text:
        return "gallery"

    if "aquarium" in category_text:
        return "aquarium"

    if "park" in category_text or "garden" in category_text:
        return "park"

    if "beach" in category_text:
        return "beach"

    if "viewpoint" in category_text:
        return "viewpoint"

    if "shopping" in category_text or "mall" in category_text:
        return "shopping"

    if "cinema" in category_text or "theatre" in category_text:
        return "entertainment"

    if "tower" in category_text or "monument" in category_text or "memorial" in category_text:
        return "landmark"

    if "tourism" in category_text or "sights" in category_text or "attraction" in category_text:
        return "attraction"

    if "waterfront" in name_lower:
        return "waterfront"

    return "place"


def enhance_place_name_and_reason(name, categories, address, forecast_list, units="imperial", city=""):
    place_type = get_place_type(name, categories)
    famous = is_famous_landmark(name, city)

    enhanced_name = name

    if place_type == "statue" and "statue" not in name.lower():
        enhanced_name = f"{name} Statue"

    if famous and "landmark" not in enhanced_name.lower():
        label = "Famous Landmark"
    else:
        label = place_type.title()

    rainy_days = sum(
        1 for day in forecast_list
        if "rain" in day["description"].lower() or "drizzle" in day["description"].lower()
    )

    avg_temp = sum(day["temp_avg"] for day in forecast_list) / len(forecast_list)
    hot_threshold = 82 if units == "imperial" else 28

    if famous:
        reason = "Top local landmark. Strong pick if you want a recognizable stop during the trip."
    elif place_type == "statue":
        reason = "Public statue or monument. Good quick sightseeing stop while exploring nearby streets."
    elif place_type == "museum":
        reason = "Museum option. Good indoor choice if the weather turns rainy, cool, or cloudy."
    elif place_type == "gallery":
        reason = "Gallery option. Good indoor stop for art, culture, or a slower-paced activity."
    elif place_type == "aquarium":
        reason = "Weather-safe attraction that works well even if outdoor plans need to move indoors."
    elif place_type == "park":
        reason = "Park option. Best if the weather stays dry and you want a walk or outdoor break."
    elif place_type == "beach":
        reason = "Beach option. Best for warm, dry weather and outdoor time."
    elif place_type == "viewpoint":
        reason = "Scenic viewpoint. Best if visibility is good and the weather stays dry."
    elif place_type == "shopping":
        reason = "Covered shopping option. Useful backup if rain moves in."
    elif place_type == "entertainment":
        reason = "Indoor or evening-friendly option that works in most weather."
    elif place_type == "landmark":
        reason = "Local landmark. Good sightseeing stop if you want something recognizable."
    else:
        reason = "Local place worth considering based on your trip location and forecast."

    if rainy_days > 0 and place_type in ["park", "beach", "viewpoint"]:
        reason += " Keep this flexible because rain is possible."

    if avg_temp >= hot_threshold and place_type in ["park", "viewpoint", "attraction"]:
        reason += " Try to go earlier or later in the day if temperatures are high."

    return {
        "name": enhanced_name,
        "reason": reason,
        "label": label,
        "type": place_type,
        "is_top_pick": False,
    }


def get_weather_reason(categories, forecast_list, units="imperial"):
    category_text = " ".join(categories).lower()

    rainy_days = sum(
        1 for day in forecast_list
        if "rain" in day["description"].lower() or "drizzle" in day["description"].lower()
    )

    avg_temp = sum(day["temp_avg"] for day in forecast_list) / len(forecast_list)

    hot_threshold = 82 if units == "imperial" else 28
    cold_threshold = 55 if units == "imperial" else 13

    if "museum" in category_text or "gallery" in category_text or "cinema" in category_text:
        return "Good indoor option if the weather turns rainy, cool, or cloudy."

    if "aquarium" in category_text:
        return "Good weather-safe attraction that works well even if plans need to move indoors."

    if "shopping" in category_text:
        return "Good covered option if rain moves in."

    if "beach" in category_text:
        return "Best for dry weather, especially if temperatures stay warm."

    if "park" in category_text:
        return "Good outdoor option if the weather stays dry."

    if "viewpoint" in category_text:
        return "Good outdoor stop if visibility is clear and the weather stays dry."

    if "sights" in category_text or "attraction" in category_text:
        return "Good sightseeing option based on the trip forecast."

    if "entertainment" in category_text:
        return "Good indoor or evening option regardless of weather."

    if rainy_days > 0:
        return "Keep this as a flexible stop depending on rain timing."

    if avg_temp >= hot_threshold:
        return "Better earlier or later in the day if temperatures are high."

    if avg_temp <= cold_threshold:
        return "Good option, but bring a layer if it involves walking outside."

    return "Good general option based on the trip forecast."


def is_low_value_place(name, categories, address=None):
    if not name:
        return True

    lower_name = name.lower()
    category_text = " ".join(categories).lower()

    if not address or address == "Address unavailable":
        return True

    blocked_name_words = [
        "highway",
        "road",
        "route",
        "corridor",
        "from ",
        " to ",
        "interstate",
        "freeway",
        "expressway",
        "turnpike",
        "parkway",
        "drive from",
        "trail from",
    ]

    if any(word in lower_name for word in blocked_name_words):
        return True

    blocked_categories = [
        "highway",
        "railway",
        "parking",
        "service.vehicle",
        "office",
        "healthcare",
        "emergency",
        "power",
        "production",
        "public_transport",
        "low_emission_zone",
        "postal_code",
        "administrative",
        "political",
    ]

    if any(blocked in category_text for blocked in blocked_categories):
        return True

    blocked_names = [
        "starbucks",
        "mcdonald",
        "subway",
        "burger king",
        "taco bell",
        "kfc",
        "wendy",
        "chipotle",
        "domino",
        "pizza hut",
        "papa john",
        "dunkin",
        "7-eleven",
        "shell",
        "chevron",
        "exxon",
        "mobil",
        "walgreens",
        "cvs",
        "rite aid",
        "target",
        "walmart",
        "costco",
        "safeway",
        "qfc",
    ]

    if any(blocked in lower_name for blocked in blocked_names):
        return True

    return False


def score_place(place):
    name = place.get("name", "").lower()
    place_type = place.get("type", "")
    is_famous = place.get("is_famous_landmark", False)

    score = 0

    if is_famous:
        score += 15

    type_scores = {
        "museum": 10,
        "aquarium": 10,
        "landmark": 9,
        "park": 8,
        "viewpoint": 8,
        "beach": 8,
        "entertainment": 6,
        "statue": 4,
        "attraction": 5,
        "shopping": 4,
    }

    score += type_scores.get(place_type, 1)

    if "museum" in name:
        score += 3
    if "park" in name:
        score += 3
    if "beach" in name:
        score += 3
    if "tower" in name:
        score += 3
    if "waterfront" in name:
        score += 3
    if "memorial" in name or "monument" in name:
        score += 2
    if "statue" in name:
        score -= 1

    return score


def fetch_geoapify_places(city, forecast_list, units="imperial"):
    coords = None

    if request.args.get("lat") and request.args.get("lon"):
        coords = {
            "lat": float(request.args.get("lat")),
            "lon": float(request.args.get("lon")),
        }
    else:
        coords = get_city_coordinates(city)
    if not coords:
        print("GEOAPIFY DEBUG: Falling back because coordinates failed.")
        return []

    categories = choose_place_categories(forecast_list, units)
    category_string = ",".join(categories)

    params = {
        "categories": category_string,
        "filter": f"circle:{coords['lon']},{coords['lat']},30000",
        "bias": f"proximity:{coords['lon']},{coords['lat']}",
        "limit": 40,
        "apiKey": GEOAPIFY_API_KEY,
    }

    try:
        response = requests.get(GEOAPIFY_PLACES_URL, params=params, timeout=10)

        print("GEOAPIFY PLACES STATUS:", response.status_code)
        print("GEOAPIFY PLACES URL:", response.url)
        print("GEOAPIFY CATEGORIES:", category_string)

        response.raise_for_status()
        data = response.json()

        features = data.get("features", [])
        print("GEOAPIFY FEATURE COUNT:", len(features))

        if not features:
            print("GEOAPIFY DEBUG: Places returned zero features.")
            print("GEOAPIFY RAW RESPONSE:", data)
            return []

        places = []

        for feature in features:
            props = feature.get("properties", {})
            name = props.get("name")
            place_categories = props.get("categories", [])

            address = (
                props.get("formatted")
                or props.get("address_line2")
                or props.get("address_line1")
                or "Address unavailable"
            )

            if is_low_value_place(name, place_categories, address):
                continue

            enhanced = enhance_place_name_and_reason(
                name=name,
                categories=place_categories,
                address=address,
                forecast_list=forecast_list,
                units=units,
                city=city,
            )

            place = {
                "name": enhanced["name"],
                "address": address,
                "categories": clean_category_list(place_categories),
                "reason": enhanced["reason"],
                "label": enhanced["label"],
                "type": enhanced["type"],
                "is_famous_landmark": is_famous_landmark(name, city),
                "is_top_pick": False,
            }

            places.append(place)

        seen_names = set()
        unique_places = []

        for place in places:
            key = place["name"].lower()

            if key in seen_names:
                continue

            seen_names.add(key)
            unique_places.append(place)

        unique_places = sorted(unique_places, key=score_place, reverse=True)

        final_places = []
        used_types = set()

        for place in unique_places:
            place_type = place.get("type", "place")

            if place_type in used_types:
                continue

            used_types.add(place_type)
            final_places.append(place)

            if len(final_places) == 3:
                break

        if len(final_places) < 3:
            for place in unique_places:
                if place not in final_places:
                    final_places.append(place)

                if len(final_places) == 3:
                    break

        if final_places:
            final_places[0]["is_top_pick"] = True

        print("GEOAPIFY NAMED PLACE COUNT:", len(final_places))

        if not final_places:
            print("GEOAPIFY DEBUG: Features existed but no useful named places remained after filtering.")
            return []

        return final_places

    except requests.RequestException as e:
        print("GEOAPIFY PLACES ERROR:", e)
        return []


def build_fallback_event_suggestions(city, forecast_list):
    rainy_days = sum(
        1 for day in forecast_list
        if "rain" in day["description"].lower() or "drizzle" in day["description"].lower()
    )

    if rainy_days > 0:
        return [
            {
                "name": "Indoor backup plan",
                "address": city,
                "categories": ["Indoor"],
                "reason": "Geoapify did not return real places, so use museums, cafes, or covered attractions as a backup.",
                "label": "Indoor",
                "type": "indoor",
                "is_top_pick": True,
            },
            {
                "name": "Local cafe or restaurant",
                "address": city,
                "categories": ["Food"],
                "reason": "Good flexible option if weather changes during the trip.",
                "label": "Food",
                "type": "food",
                "is_top_pick": False,
            },
            {
                "name": "Covered attraction",
                "address": city,
                "categories": ["Attraction"],
                "reason": "Useful backup plan if outdoor conditions are not ideal.",
                "label": "Attraction",
                "type": "attraction",
                "is_top_pick": False,
            },
        ]

    return [
        {
            "name": "Outdoor attraction",
            "address": city,
            "categories": ["Outdoor"],
            "reason": "Geoapify did not return real places, so use this as a general outdoor backup.",
            "label": "Outdoor",
            "type": "outdoor",
            "is_top_pick": True,
        },
        {
            "name": "Local park or viewpoint",
            "address": city,
            "categories": ["Park"],
            "reason": "Good fit for mild or sunny trip conditions.",
            "label": "Park",
            "type": "park",
            "is_top_pick": False,
        },
        {
            "name": "Walkable local area",
            "address": city,
            "categories": ["Sightseeing"],
            "reason": "Good flexible plan for exploring without overcommitting.",
            "label": "Sightseeing",
            "type": "sightseeing",
            "is_top_pick": False,
        },
    ]


def build_real_place_recommendations(city, forecast_list, units="imperial"):
    real_places = fetch_geoapify_places(city, forecast_list, units)

    if real_places:
        return real_places

    return build_fallback_event_suggestions(city, forecast_list)


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
            "best_indoor_day": None,
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
        "best_indoor_day": best_indoor["date"],
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
                "time_slots": [],
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
            "icon": item["weather"][0]["icon"],
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
            "time_slots": values["time_slots"],
        })

    return sorted(result, key=lambda x: x["date"])


@app.route("/api/trip-weather")
def trip_weather():
    city = request.args.get("city")
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    start = request.args.get("start")
    end = request.args.get("end")
    units = request.args.get("units", "imperial")

    if not (city or (lat and lon)) or not start or not end:
        return jsonify({"error": "City and trip dates are required."}), 400

    if not OPENWEATHER_API_KEY:
        return jsonify({"error": "Missing OpenWeather API key."}), 500

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

    if lat and lon:
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": units,
        }
    else:
        params = {
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": units,
        }

    try:
        response = requests.get(OPENWEATHER_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        weather_data = response.json()
    except requests.HTTPError:
        return jsonify({
            "error": "City not found. Try another destination or check the spelling.",
        }), 404
    except requests.RequestException:
        return jsonify({
            "error": "Weather service unavailable right now. Try again in a moment.",
        }), 500

    filtered_entries = [
        item for item in weather_data.get("list", [])
        if start_date <= datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S").date() <= end_date
    ]

    if not filtered_entries:
        return jsonify({
            "error": "This planner currently supports trips in the next 5 days because of the weather API forecast limit.",
        }), 400

    daily_forecast = summarize_daily_forecast(filtered_entries)
    best_days = get_best_days(daily_forecast)

    return jsonify({
        "destination": request.args.get("city") or "Selected location",
        "forecast": daily_forecast,
        "packing_suggestions": build_packing_suggestions(daily_forecast, units),
        "event_suggestions": build_real_place_recommendations(city, daily_forecast, units),
        "summary": build_summary(city, daily_forecast),
        "trip_label": get_trip_label(daily_forecast),
        "best_outdoor_day": best_days["best_outdoor_day"],
        "best_indoor_day": best_days["best_indoor_day"],
        "units": units,
    })


if __name__ == "__main__":
    app.run(debug=True)