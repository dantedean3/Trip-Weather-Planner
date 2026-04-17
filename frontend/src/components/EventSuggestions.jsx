export default function EventSuggestions({ suggestions }) {
  if (!suggestions || suggestions.length === 0) return null;

  return (
    <div className="section event-box">
      <h2>Things To Do</h2>
      <p>Based on the weather, here are a few low-stress ideas for the trip:</p>
      <ul className="event-list">
        {suggestions.map((item, index) => (
          <li key={index}>🎯 {item}</li>
        ))}
      </ul>
    </div>
  );
}