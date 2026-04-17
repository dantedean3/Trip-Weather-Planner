import { useEffect, useState } from "react";
import TripForm from "./components/TripForm";
import ForecastList from "./components/ForecastList";
import PackingSuggestions from "./components/PackingSuggestions";
import TripSummary from "./components/TripSummary";
import RecentSearches from "./components/RecentSearches";
import TemperatureChart from "./components/TemperatureChart";
import EventSuggestions from "./components/EventSuggestions";
import CityHero from "./components/CityHero";
import LoadingPanel from "./components/LoadingPanel";
import "./index.css";

export default function App() {
  const [tripData, setTripData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [recentSearches, setRecentSearches] = useState([]);

  useEffect(() => {
    const saved = localStorage.getItem("recentTripSearches");
    if (saved) {
      try {
        setRecentSearches(JSON.parse(saved));
      } catch {
        setRecentSearches([]);
      }
    }
  }, []);

  function saveRecentSearch(formData) {
    const cleaned = {
      city: formData.city.trim(),
      start: formData.start,
      end: formData.end,
      units: formData.units,
    };

    const updated = [
      cleaned,
      ...recentSearches.filter(
        (item) =>
          !(
            item.city.toLowerCase() === cleaned.city.toLowerCase() &&
            item.start === cleaned.start &&
            item.end === cleaned.end &&
            item.units === cleaned.units
          )
      ),
    ].slice(0, 6);

    setRecentSearches(updated);
    localStorage.setItem("recentTripSearches", JSON.stringify(updated));
  }

  function clearRecentSearches() {
    setRecentSearches([]);
    localStorage.removeItem("recentTripSearches");
  }

  async function fetchTripWeather(formData) {
    setLoading(true);
    setError("");
    setTripData(null);

    const params = new URLSearchParams(formData).toString();

    try {
      const response = await fetch(`http://127.0.0.1:5000/api/trip-weather?${params}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Something went wrong.");
      }

      setTripData(data);
      saveRecentSearch(formData);
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  function handleRecentSearchClick(search) {
    fetchTripWeather(search);
  }

  return (
    <div className="app">
      <div className="container">
        <h1>Trip Weather Planner</h1>
        <p className="subtitle">
          Plan your trip, check the forecast, and get packing suggestions.
        </p>

        <TripForm onSubmit={fetchTripWeather} />

        <RecentSearches
          recentSearches={recentSearches}
          onSelect={handleRecentSearchClick}
          onClear={clearRecentSearches}
        />

        {loading && <LoadingPanel />}
        {error && <p className="error">{error}</p>}

        {!loading && !tripData && !error && (
          <div className="section empty-state-box">
            <h2>Ready to plan your trip</h2>
            <p>Search a city and choose your dates to see weather, packing tips, and a few trip ideas.</p>
          </div>
        )}

        {tripData && (
          <>
            <CityHero city={tripData.destination} tripLabel={tripData.trip_label} forecast={tripData.forecast} />

            <div className="top-panels">
              <TripSummary
                summary={tripData.summary}
                forecast={tripData.forecast}
                tripLabel={tripData.trip_label}
                bestOutdoorDay={tripData.best_outdoor_day}
                bestIndoorDay={tripData.best_indoor_day}
              />
              <PackingSuggestions suggestions={tripData.packing_suggestions} />
            </div>

            <EventSuggestions suggestions={tripData.event_suggestions} />

            <TemperatureChart
              forecast={tripData.forecast}
              units={tripData.units}
              destination={tripData.destination}
            />

            <ForecastList forecast={tripData.forecast} units={tripData.units} />
          </>
        )}
      </div>
    </div>
  );
}