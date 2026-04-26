export default function EventSuggestions({ suggestions }) {
  if (!suggestions || suggestions.length === 0) return null;

  return (
    <div className="section event-box">
      <h2>Things To Do</h2>
      <p>Real nearby places selected based on the trip weather:</p>

      <div className="event-card-list">
        {suggestions.map((item, index) => {
          const isObject = typeof item === "object" && item !== null;

          if (!isObject) {
            return (
              <div className="event-card" key={index}>
                <h3>Suggestion</h3>
                <p>{item}</p>
              </div>
            );
          }

          return (
            <div
              className={`event-card ${item.is_top_pick ? "top-pick-card" : ""}`}
              key={`${item.name || "place"}-${index}`}
            >
              <h3>{item.name || "Recommended place"}</h3>

              {item.is_top_pick && (
                <p className="top-pick-text">Top Pick</p>
              )}

              {item.address && (
                <p className="event-address">{item.address}</p>
              )}

              {item.reason && <p>{item.reason}</p>}
            </div>
          );
        })}
      </div>
    </div>
  );
}