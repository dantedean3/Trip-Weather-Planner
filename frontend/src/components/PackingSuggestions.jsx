const iconMap = {
  sunscreen: "🧴",
  sunglasses: "🕶️",
  hat: "🧢",
  umbrella: "☔",
  raincoat: "🧥",
  "rain boots": "🥾",
  jacket: "🧥",
  hoodie: "👕",
  windbreaker: "🌬️",
  "water bottle": "💧",
  "walking shoes": "👟",
  "comfortable walking shoes": "👟",
  layers: "🧣",
  pants: "👖",
};

function getIcon(text) {
  const lower = text.toLowerCase();
  for (const key in iconMap) {
    if (lower.includes(key)) return iconMap[key];
  }
  return "✔️";
}

export default function PackingSuggestions({ suggestions }) {
  return (
    <div className="section packing-box top-panel-card">
      <h2>Packing Suggestions</h2>
      <p>Based on the forecast, here’s what you should bring:</p>
      <ul className="packing-list">
        {suggestions.map((item, index) => (
          <li key={index}>
            <span className="packing-icon">{getIcon(item)}</span>
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}