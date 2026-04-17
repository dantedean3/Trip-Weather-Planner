export default function CityHero({ city, tripLabel, forecast }) {
  if (!city) return null;

  function normalizeCity(cityName) {
    return cityName.trim().toLowerCase();
  }

  function getCityImage(cityName) {
    const normalized = normalizeCity(cityName);

    const cityImages = {
      "seattle": "https://images.unsplash.com/photo-1502175353174-a7a70e73b362?auto=format&fit=crop&w=1600&q=80",
      "washington dc": "https://images.unsplash.com/photo-1617581629397-a72507c3de9e?auto=format&fit=crop&w=1600&q=80",
      "washington, dc": "https://images.unsplash.com/photo-1617581629397-a72507c3de9e?auto=format&fit=crop&w=1600&q=80",
      "toronto": "https://images.unsplash.com/photo-1517090504586-fde19ea6066f?auto=format&fit=crop&w=1600&q=80",
      "nassau": "https://images.unsplash.com/photo-1589197331516-4d84b8af0d7a?auto=format&fit=crop&w=1600&q=80",
      "nassau bahamas": "https://images.unsplash.com/photo-1589197331516-4d84b8af0d7a?auto=format&fit=crop&w=1600&q=80",
      "salem": "https://images.unsplash.com/photo-1577415124269-fc1140a69e91?auto=format&fit=crop&w=1600&q=80",
      "salem oregon": "https://images.unsplash.com/photo-1577415124269-fc1140a69e91?auto=format&fit=crop&w=1600&q=80",
      "tampa": "https://images.unsplash.com/photo-1514214246283-d427a95c5d2f?auto=format&fit=crop&w=1600&q=80",
      "key west": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1600&q=80",
      "phoenix": "https://images.unsplash.com/photo-1570553211395-3f3c8e8ed90b?auto=format&fit=crop&w=1600&q=80",
      "orlando": "https://images.unsplash.com/photo-1514214246283-d427a95c5d2f?auto=format&fit=crop&w=1600&q=80",
      "atlanta": "https://images.unsplash.com/photo-1575917649662-7c1d4dfc0f3b?auto=format&fit=crop&w=1600&q=80",
      "houston": "https://images.unsplash.com/photo-1531218150217-54595bc2b934?auto=format&fit=crop&w=1600&q=80",
      "portland": "https://images.unsplash.com/photo-1559144154-4b46d03327d3?auto=format&fit=crop&w=1600&q=80",
      "portland oregon": "https://images.unsplash.com/photo-1559144154-4b46d03327d3?auto=format&fit=crop&w=1600&q=80",
      "new york": "https://images.unsplash.com/photo-1496588152823-86ff7695e68f?auto=format&fit=crop&w=1600&q=80",
      "new york city": "https://images.unsplash.com/photo-1496588152823-86ff7695e68f?auto=format&fit=crop&w=1600&q=80",
      "chicago": "https://images.unsplash.com/photo-1494522855154-9297ac14b55f?auto=format&fit=crop&w=1600&q=80",
    };

    return (
      cityImages[normalized] ||
      "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=1600&q=80"
    );
  }

  const imageUrl = getCityImage(city);
  const tripDuration = forecast?.length || 0;

  return (
    <div className="city-hero">
      <img
        src={imageUrl}
        alt={city}
        onError={(e) => {
          e.currentTarget.src =
            "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=1600&q=80";
        }}
      />
      <div className="hero-overlay">
        <div className="hero-text-block">
          <h2>{city}</h2>
          <div className="hero-badges">
            <span className="hero-badge">{tripDuration}-day trip</span>
            <span className="hero-badge hero-weather-badge">{tripLabel}</span>
          </div>
        </div>
      </div>
    </div>
  );
}