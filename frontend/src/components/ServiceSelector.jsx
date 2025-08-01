export default function ServiceSelector({ services, service, onChange, onFetch }) {
  return (
    <div className="service-selector">
      <select
        value={service}
        onChange={(e) => onChange(e.target.value)}
      >
        {services.map((s) => (
          <option key={s.value} value={s.value}>
            {s.label}
          </option>
        ))}
      </select>
      
    </div>
  );
}