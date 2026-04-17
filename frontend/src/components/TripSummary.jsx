export default function TripSummary({
  summary,
  forecast,
  tripLabel,
  bestOutdoorDay,
  bestIndoorDay
}) {
  function formatDate(dateString) {
    if (!dateString) return "Not available";
    const date = new Date(`${dateString}T12:00:00`);
    return date.toLocaleDateString("en-US", {
      weekday: "long",
      month: "short",
      day: "numeric",
    });
  }

  const tripDuration = forecast?.length || 0;

  return (
    <div className="section summary-box top-panel-card">
      <div className="summary-top-row">
        <h2>Trip Summary</h2>
        <div className="summary-badges">
          <span className="trip-duration-badge">
            {tripDuration}-day trip
          </span>
          <span className="trip-label-badge">
            {tripLabel}
          </span>
        </div>
      </div>

      <p>{summary}</p>

      <div className="best-days-box">
        <p><strong>Best day to be outside:</strong> {formatDate(bestOutdoorDay)}</p>
        <p><strong>Best day for indoor plans:</strong> {formatDate(bestIndoorDay)}</p>
      </div>
    </div>
  );
}