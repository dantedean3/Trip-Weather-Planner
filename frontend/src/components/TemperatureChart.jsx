export default function TemperatureChart({ forecast, units, destination }) {
  if (!forecast || !forecast.length) return null;

  const tempUnit = units === "metric" ? "°C" : "°F";
  const maxTemp = Math.max(...forecast.map((day) => day.temp_max));
  const minTemp = Math.min(...forecast.map((day) => day.temp_min));
  const range = Math.max(maxTemp - minTemp, 1);

  function formatShortDate(dateString) {
    const date = new Date(`${dateString}T12:00:00`);
    return date.toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
    });
  }

  return (
    <div className="section chart-box">
      <div className="chart-header">
        <h2>Temperature Trend</h2>
        <p>{destination} trip forecast</p>
      </div>

      <div className="temp-chart">
        {forecast.map((day, index) => {
          const avgHeight = ((day.temp_avg - minTemp) / range) * 120 + 30;
          const maxHeight = ((day.temp_max - minTemp) / range) * 120 + 30;
          const minHeight = ((day.temp_min - minTemp) / range) * 120 + 30;

          return (
            <div className="temp-chart-column" key={index}>
              <div className="temp-values">
                <span className="temp-max">{Math.round(day.temp_max)}{tempUnit}</span>
                <span className="temp-min">{Math.round(day.temp_min)}{tempUnit}</span>
              </div>

              <div className="temp-bar-stack">
                <div
                  className="temp-bar max-bar"
                  style={{ height: `${maxHeight}px` }}
                  title={`High: ${day.temp_max}${tempUnit}`}
                />
                <div
                  className="temp-bar avg-bar"
                  style={{ height: `${avgHeight}px` }}
                  title={`Average: ${day.temp_avg}${tempUnit}`}
                />
                <div
                  className="temp-bar min-bar"
                  style={{ height: `${minHeight}px` }}
                  title={`Low: ${day.temp_min}${tempUnit}`}
                />
              </div>

              <div className="temp-date">{formatShortDate(day.date)}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}