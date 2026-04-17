import { useState } from "react";

export default function ForecastList({ forecast, units }) {
  const [openIndex, setOpenIndex] = useState(null);

  const tempUnit = units === "metric" ? "°C" : "°F";
  const windUnit = units === "metric" ? "m/s" : "mph";

  function toggleCard(index) {
    setOpenIndex(openIndex === index ? null : index);
  }

  function formatDate(dateString) {
    const date = new Date(`${dateString}T12:00:00`);
    return date.toLocaleDateString("en-US", {
      weekday: "long",
      month: "short",
      day: "numeric",
    });
  }

  function getWeatherClass(condition = "") {
    const value = condition.toLowerCase();

    if (value.includes("clear")) return "sunny-card";
    if (value.includes("rain") || value.includes("drizzle")) return "rainy-card";
    if (value.includes("cloud")) return "cloudy-card";
    if (value.includes("snow")) return "snow-card";
    if (value.includes("thunder")) return "storm-card";

    return "default-card";
  }

  function getWeatherAccent(condition = "") {
    const value = condition.toLowerCase();

    if (value.includes("clear")) return "☀️";
    if (value.includes("rain") || value.includes("drizzle")) return "🌧️";
    if (value.includes("cloud")) return "☁️";
    if (value.includes("snow")) return "❄️";
    if (value.includes("thunder")) return "⛈️";

    return "🌤️";
  }

  return (
    <div className="section">
      <h2>Forecast</h2>
      <div className="forecast-grid">
        {forecast.map((item, index) => {
          const isOpen = openIndex === index;

          return (
            <div
              className={`forecast-card ${getWeatherClass(item.condition)} ${isOpen ? "open" : ""}`}
              key={index}
            >
              <div className="forecast-card-header">
                <h3>{formatDate(item.date)}</h3>

                <img
                  src={`https://openweathermap.org/img/wn/${item.icon}@2x.png`}
                  alt={item.description}
                  className="weather-icon"
                />

                <p className="condition">
                  <span className="condition-accent">
                    {getWeatherAccent(item.condition)}
                  </span>
                  <strong>{item.condition}</strong>
                </p>

                <p className="description">{item.description}</p>

                <div className="forecast-main-stats">
                  <p>High: {item.temp_max}{tempUnit}</p>
                  <p>Low: {item.temp_min}{tempUnit}</p>
                  <p>Average: {item.temp_avg}{tempUnit}</p>
                </div>

                <p className="hint">Click to view hourly details</p>

                <button
                  type="button"
                  className="details-button"
                  onClick={() => toggleCard(index)}
                >
                  {isOpen ? "Hide details" : "View details"}
                  <span className={`arrow ${isOpen ? "rotate" : ""}`}>⌄</span>
                </button>
              </div>

              <div className={`details-wrapper ${isOpen ? "expanded" : ""}`}>
                <div className="time-slot-list">
                  <h4>Weather by time</h4>

                  {item.time_slots.map((slot, slotIndex) => (
                    <div className="time-slot-card" key={slotIndex}>
                      <div className="time-slot-top">
                        <span className="time-slot-time">{slot.time}</span>
                        <img
                          src={`https://openweathermap.org/img/wn/${slot.icon}.png`}
                          alt={slot.description}
                          className="time-slot-icon"
                        />
                      </div>

                      <p>
                        <span className="condition-accent small-accent">
                          {getWeatherAccent(slot.condition)}
                        </span>
                        <strong>{slot.condition}</strong> ({slot.description})
                      </p>

                      <p>Temp: {slot.temp}{tempUnit}</p>
                      <p>High: {slot.temp_max}{tempUnit}</p>
                      <p>Low: {slot.temp_min}{tempUnit}</p>
                      <p>Humidity: {slot.humidity}%</p>
                      <p>Wind: {slot.wind_speed} {windUnit}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}