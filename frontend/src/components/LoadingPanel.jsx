export default function LoadingPanel() {
  return (
    <div className="section loading-box">
      <div className="loading-row">
        <div className="spinner" />
        <div>
          <h2>Loading your trip weather...</h2>
          <p>Pulling forecast data and building suggestions.</p>
        </div>
      </div>

      <div className="loading-skeleton-grid">
        <div className="skeleton-card" />
        <div className="skeleton-card" />
        <div className="skeleton-card" />
      </div>
    </div>
  );
}