import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell
} from "recharts";

const COLORS = ["#06d6a0", "#3b82f6", "#ef4444"];

function renderSummary(text) {
  const lines = text.split("\n").filter((line) => line.trim() !== "");
  const elements = [];
  let listItems = [];

  lines.forEach((line) => {
    const trimmed = line.trim();
    if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      listItems.push(trimmed.slice(2));
    } else {
      if (listItems.length) {
        elements.push(
          <ul key={`list-${elements.length}`}>
            {listItems.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        );
        listItems = [];
      }
      elements.push(<p key={`p-${elements.length}`}>{line}</p>);
    }
  });

  if (listItems.length) {
    elements.push(
      <ul key={`list-${elements.length}`}>
        {listItems.map((item, idx) => (
          <li key={idx}>{item}</li>
        ))}
      </ul>
    );
  }

  return elements;
}

export default function AIReport({ summary, sentiment, stats }) {
  if (!summary && !sentiment && !stats) {
    return <p className="no-content">Aucun rapport disponible.</p>;
  }

  const sentimentData = stats
    ? Object.entries(stats.sentiment || {}).map(([name, value]) => ({
        name,
        value,
      }))
    : [];
  return (
    <div className="ai-report">
      {summary && <div className="report-summary">{renderSummary(summary)}</div>}
      {sentiment && (
        <p className="report-sentiment">Sentiment&nbsp;: {sentiment}</p>
      )}

      {stats && (
        <div className="ai-stats">
          <section className="kpi-grid">
            <div className="metric-card">
              <div className="metric-label">Mentions</div>
              <div className="metric-value">{stats.totalMentions}</div>
            </div>
          </section>

          {stats.topSources?.length > 0 && (
            <div className="chart-card">
              <h3 className="chart-title">Top sources</h3>
              <ul className="top-sources">
                {stats.topSources.map((s) => (
                  <li key={s.name}>
                    {s.name}: {s.count}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {stats.timeline?.length > 0 && (
            <div className="chart-card">
              <h3 className="chart-title">Évolution temporelle</h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={stats.timeline}>
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#06d6a0" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {sentimentData.length > 0 && (
            <div className="chart-card">
              <h3 className="chart-title">Répartition du sentiment</h3>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={sentimentData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label
                  >
                    {sentimentData.map((entry, index) => (
                      <Cell
                        key={`cell-${entry.name}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}
    </div>
  );
}