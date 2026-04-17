# Trip Weather Planner

A full-stack web application that helps users plan short trips using real-time weather data, packing suggestions, and smart recommendations.

## 🌐 Live Demo
https://trip-weather-planner.vercel.app/

## 📦 Tech Stack
- Frontend: React (Vite)
- Backend: Flask (Python)
- API: OpenWeather API
- Deployment:
  - Frontend → Vercel
  - Backend → Render

---

## 🚀 Features

### Weather Forecasting
- 5-day forecast using live API data
- Daily + hourly breakdown
- Expandable forecast cards with scrollable time slots

### Trip Intelligence
- “Best day to be outside”
- “Best day for indoor plans”
- Automatic trip classification (Sunny, Rainy, Mixed, Cool)

### Smart Suggestions
- Packing recommendations based on weather
- Event/activity suggestions based on conditions
- City-aware enhancements (landmarks, travel patterns)

### UI / UX
- Dynamic header that changes color based on weather
- Temperature trend visualization
- Recent search persistence using localStorage
- Smooth animations and expandable components

---

## 📸 Screenshots

### Entry + Search
![Entry](assets/projects/tw-entry.png)

### Main View
![Main](assets/projects/tw-search.png)

### Forecast Details
![Forecast](assets/projects/tw-forecast.png)

### Temperature Trend
![Trend](assets/projects/tw-trend.png)

### Recommendations
![Events](assets/projects/tw-events.png)

---

## 🧠 Why I Built This

Most weather apps show raw data.  
This project focuses on **decision-making**:

- What should I pack?
- What should I do?
- Which day is best for plans?

It turns weather data into something actually useful for planning a trip.

---

## ⚙️ Local Setup

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt


⚠️ Notes
Weather API only supports ~5 days ahead
Frontend includes validation to prevent invalid date ranges
