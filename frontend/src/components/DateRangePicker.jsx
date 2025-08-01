export default function DateRangePicker({ start, end, onChange }) {
  return (
    <div className="date-picker-container">
      <div className="date-input-group">
        <label htmlFor="start-date">Du</label>
        <input
          id="start-date"
          type="date"
          value={start}
          onChange={(e) => onChange('start', e.target.value)}
          className="date-input"
        />
      </div>
      <div className="date-input-group">
        <label htmlFor="end-date">Au</label>
        <input
          id="end-date"
          type="date"
          value={end}
          onChange={(e) => onChange('end', e.target.value)}
          className="date-input"
        />
      </div>
    </div>
  );
}