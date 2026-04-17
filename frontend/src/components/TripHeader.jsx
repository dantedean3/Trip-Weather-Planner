export default function TripHeader({ destination, tripLabel, days }) {
  function getHeaderStyle(label) {
    if (!label) {
      return {
        background: "linear-gradient(135deg, #4f8cff, #6ed0ff)",
      };
    }

    const lower = label.toLowerCase();

    if (lower.includes("sunny")) {
      return {
        background: "linear-gradient(135deg, #f6d365, #fda085)",
      };
    }

    if (lower.includes("rain")) {
      return {
        background: "linear-gradient(135deg, #4facfe, #00f2fe)",
      };
    }

    if (lower.includes("cool") || lower.includes("cold")) {
      return {
        background: "linear-gradient(135deg, #a1c4fd, #c2e9fb)",
      };
    }

    if (lower.includes("mixed")) {
      return {
        background: "linear-gradient(135deg, #667eea, #764ba2)",
      };
    }

    return {
      background: "linear-gradient(135deg, #4f8cff, #6ed0ff)",
    };
  }

  function getHeaderIcon(label) {
    if (!label) return "🌤️";

    const lower = label.toLowerCase();

    if (lower.includes("sunny")) return "☀️";
    if (lower.includes("rain")) return "🌧️";
    if (lower.includes("cool") || lower.includes("cold")) return "❄️";
    if (lower.includes("mixed")) return "⛅";

    return "🌤️";
  }

  return (
    <div className="trip-header" style={getHeaderStyle(tripLabel)}>
      <div className="trip-header-content">
        <div className="trip-header-title-row">
          <span className="trip-header-icon">{getHeaderIcon(tripLabel)}</span>
          <h2>{destination}</h2>
        </div>
        <p>
          {days}-day trip • {tripLabel}
        </p>
      </div>
    </div>
  );
}