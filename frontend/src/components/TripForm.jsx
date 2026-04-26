import { useMemo, useState } from "react";

function formatLocalDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export default function TripForm({ onSubmit }) {
  const [formData, setFormData] = useState({
    city: "",
    start: "",
    end: "",
    units: "imperial",
  });

  const [formError, setFormError] = useState("");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [selectedPlace, setSelectedPlace] = useState(null);

  const { minDate, maxDate } = useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const maxForecastDate = new Date(today);
    maxForecastDate.setDate(maxForecastDate.getDate() + 5);

    return {
      minDate: formatLocalDate(today),
      maxDate: formatLocalDate(maxForecastDate),
    };
  }, []);

  function handleChange(e) {
    const { name, value } = e.target;

    let updatedFormData = {
      ...formData,
      [name]: value,
    };

    if (name === "start") {
      if (value < minDate) {
        updatedFormData.start = minDate;
      }
      if (value > maxDate) {
        updatedFormData.start = maxDate;
      }
      if (updatedFormData.end && updatedFormData.end < updatedFormData.start) {
        updatedFormData.end = updatedFormData.start;
      }
    }

    if (name === "end") {
      if (value < (updatedFormData.start || minDate)) {
        updatedFormData.end = updatedFormData.start || minDate;
      }
      if (value > maxDate) {
        updatedFormData.end = maxDate;
      }
    }

    setFormData(updatedFormData);
    setFormError("");
  }

  async function fetchSuggestions(value) {
    setQuery(value);
    setSelectedPlace(null);

    if (value.length < 2) {
      setResults([]);
      return;
    }

    const res = await fetch(
      `https://api.geoapify.com/v1/geocode/autocomplete?text=${value}&limit=5&apiKey=a7aeceaadf8e4d99af2015713a9f2007`
    );

    const data = await res.json();
    setResults(data.features || []);
  }

  function handleSubmit(e) {
    e.preventDefault();

    if (formData.end < formData.start) {
      setFormError("End date cannot be earlier than start date.");
      return;
    }

    if (formData.start < minDate || formData.end < minDate) {
      setFormError("Please choose today or a future date.");
      return;
    }

    if (formData.start > maxDate || formData.end > maxDate) {
      setFormError("This app currently supports trips within the next 5 days.");
      return;
    }

    onSubmit({
      ...formData,
      city: selectedPlace?.name || query,
      lat: selectedPlace?.lat,
      lon: selectedPlace?.lon,
    });
  }

  return (
    <>
      <form className="trip-form" onSubmit={handleSubmit}>
        {/* AUTOCOMPLETE INPUT */}
        <div className="autocomplete-wrapper">
          <input
            type="text"
            placeholder="Enter destination city"
            value={query}
            onChange={(e) => fetchSuggestions(e.target.value)}
            required
          />

          {results.length > 0 && (
            <div className="autocomplete-dropdown">
              {results.map((item, i) => {
                const props = item.properties;

                return (
                  <div
                    key={i}
                    className="autocomplete-item"
                    onClick={() => {
                      setSelectedPlace({
                        name: props.formatted,
                        lat: props.lat,
                        lon: props.lon,
                      });

                      setQuery(props.formatted);
                      setResults([]);

                      setFormData((prev) => ({
                        ...prev,
                        city: props.formatted,
                      }));
                    }}
                  >
                    {props.formatted}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* DATES */}
        <input
          type="date"
          name="start"
          value={formData.start}
          onChange={handleChange}
          min={minDate}
          max={maxDate}
          required
        />

        <input
          type="date"
          name="end"
          value={formData.end}
          onChange={handleChange}
          min={formData.start || minDate}
          max={maxDate}
          required
        />

        {/* UNITS */}
        <select name="units" value={formData.units} onChange={handleChange}>
          <option value="imperial">Imperial (°F)</option>
          <option value="metric">Metric (°C)</option>
        </select>

        <button type="submit">Get Forecast</button>
      </form>

      {formError && <p className="error">{formError}</p>}
    </>
  );
}