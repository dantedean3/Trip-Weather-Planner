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

    onSubmit(formData);
  }

  return (
    <>
      <form className="trip-form" onSubmit={handleSubmit}>
        <input
          type="text"
          name="city"
          placeholder="Enter destination city"
          value={formData.city}
          onChange={handleChange}
          required
        />

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