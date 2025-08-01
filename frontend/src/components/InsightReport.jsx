import React, { useMemo } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
} from "recharts";

// Palette for pie slices - couleurs améliorées
const COLORS = [
  "#06d6a0",
  "#3b82f6", 
  "#8b5cf6",
  "#ef4444",
  "#f97316",
  "#eab308",
  "#22c55e",
  "#14b8a6",
  "#f59e0b",
  "#84cc16"
];

// ────────────────────────────────────────────────────────────────────────────────
// Extract metrics (now groups by article.service OR hostname)                    
// ────────────────────────────────────────────────────────────────────────────────
function useMetrics(articles = []) {
  return useMemo(() => {
    const m = {
      total: articles.length,
      byYear: {},
      bySource: {},
      firstDate: null,
      lastDate: null,
    };

    articles.forEach((a) => {
      // Year bucket
      const d = new Date(a.date);
      if (!isNaN(d)) {
        const y = d.getFullYear();
        m.byYear[y] = (m.byYear[y] || 0) + 1;
        if (!m.firstDate || d < m.firstDate) m.firstDate = d;
        if (!m.lastDate || d > m.lastDate) m.lastDate = d;
      }

      // Source bucket → priority: article.service (added in App.jsx) else hostname else « Unknown »
      let key = a.service;
      if (!key) {
        if (a.url) {
          try {
            key = new URL(a.url).host;
          } catch {
            /* ignore */
          }
        }
      }
      if (!key) key = "Inconnu";
      m.bySource[key] = (m.bySource[key] || 0) + 1;
    });

    return m;
  }, [articles]);
}

// Composant Tooltip personnalisé pour le graphique en barres
const CustomBarTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="custom-chart-tooltip">
        <p className="tooltip-label">{`Année: ${label}`}</p>
        <p className="tooltip-value">
          <span className="tooltip-dot" style={{ backgroundColor: '#06d6a0' }}></span>
          {`Articles: ${payload[0].value}`}
        </p>
      </div>
    );
  }
  return null;
};

// Composant Tooltip personnalisé pour le graphique en camembert
const CustomPieTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0];
    return (
      <div className="custom-chart-tooltip">
        <p className="tooltip-label">{data.name}</p>
        <p className="tooltip-value">
          <span className="tooltip-dot" style={{ backgroundColor: data.color }}></span>
          {`Articles: ${data.value}`}
        </p>
      </div>
    );
  }
  return null;
};

// ────────────────────────────────────────────────────────────────────────────────
// Component                                                                        
// ────────────────────────────────────────────────────────────────────────────────
export default function InsightReport({ articles }) {
  const { total, byYear, bySource, firstDate, lastDate } = useMetrics(articles);

  const yearlyData = Object.entries(byYear)
    .map(([year, value]) => ({ year, value }))
    .sort((a, b) => Number(a.year) - Number(b.year));

  const sourceData = Object.entries(bySource)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 8);

  if (!articles.length) return <p className="no-content">No data available yet.</p>;

  const yearsSpan = firstDate && lastDate ? `${firstDate.getFullYear()} – ${lastDate.getFullYear()}` : "n/a";

  return (
    <div className="report-wrapper">
      {/* KPIs */}
      <section className="kpi-grid">
        <MetricCard label="Articles" value={total} />
        <MetricCard label="Période" value={yearsSpan} />
        <MetricCard label="Sources uniques" value={Object.keys(bySource).length} />
        <MetricCard label="Moyenne / an" value={yearlyData.length ? (total / yearlyData.length).toFixed(1) : "n/a"} />
      </section>

      {/* Charts */}
      <div className="charts">
        <ChartCard title="Articles par an">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={yearlyData} margin={{ top: 20, right: 30, left: 0, bottom: 20 }}>
              <XAxis 
                dataKey="year" 
                tick={{ fill: '#e2e8f0', fontSize: 12 }}
                axisLine={{ stroke: '#334155' }}
                tickLine={{ stroke: '#334155' }}
              />
              <YAxis 
                allowDecimals={false}
                tick={{ fill: '#e2e8f0', fontSize: 12 }}
                axisLine={{ stroke: '#334155' }}
                tickLine={{ stroke: '#334155' }}
              />
              <Tooltip content={<CustomBarTooltip />} />
              <Bar 
                dataKey="value" 
                fill="#06d6a0"
                radius={[4, 4, 0, 0]}
                style={{
                  filter: 'drop-shadow(0 4px 6px rgba(6, 214, 160, 0.3))'
                }}
              />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {sourceData.length > 0 && (
          <ChartCard title="Top 8 sources">
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie 
                  data={sourceData} 
                  dataKey="value" 
                  nameKey="name" 
                  cx="50%" 
                  cy="50%" 
                  outerRadius={100}
                  innerRadius={30}
                  paddingAngle={2}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  labelLine={false}
                  style={{
                    fontSize: '12px',
                    fill: '#e2e8f0'
                  }}
                >
                  {sourceData.map((entry, index) => (
                    <Cell 
                      key={entry.name} 
                      fill={COLORS[index % COLORS.length]}
                      style={{
                        filter: 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3))',
                        cursor: 'pointer'
                      }}
                    />
                  ))}
                </Pie>
                <Tooltip content={<CustomPieTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>
        )}
      </div>
    </div>
  );
}

// KPI + chart card UI
const MetricCard = ({ label, value }) => (
  <div className="metric-card">
    <span className="metric-value">{value}</span>
    <span className="metric-label">{label}</span>
  </div>
);

const ChartCard = ({ title, children }) => (
  <div className="chart-card">
    <h3 className="chart-title">{title}</h3>
    <div className="chart-content">
      {children}
    </div>
  </div>
);