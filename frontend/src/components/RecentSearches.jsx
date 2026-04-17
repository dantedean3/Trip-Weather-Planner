export default function RecentSearches({ recentSearches, onSelect, onClear }) {
  return (
    <div className="section recent-searches-box">
      <div className="recent-searches-header">
        <div>
          <h2>Recent Searches</h2>
          <p>
            {recentSearches.length
              ? "Click one to run it again."
              : "No recent searches yet."}
          </p>
        </div>

        {recentSearches.length > 0 && (
          <button type="button" className="clear-recent-btn" onClick={onClear}>
            Clear recent searches
          </button>
        )}
      </div>

      {recentSearches.length > 0 && (
        <div className="recent-searches-list">
          {recentSearches.map((search, index) => (
            <button
              key={`${search.city}-${search.start}-${search.end}-${index}`}
              className="recent-search-chip"
              type="button"
              onClick={() => onSelect(search)}
            >
              <span className="chip-city">{search.city}</span>
              <span className="chip-dates">
                {search.start} → {search.end}
              </span>
              <span className="chip-units">
                {search.units === "imperial" ? "°F" : "°C"}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}