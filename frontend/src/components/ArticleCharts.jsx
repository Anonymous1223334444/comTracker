import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip,
  PieChart, Pie, Cell
} from 'recharts';

// Palette de couleurs pour les graphiques
const COLORS = ['#06d6a0', '#3b82f6', '#8b5cf6', '#ef4444', '#f97316', '#eab308', '#22c55e', '#14b8a6'];

function timelineData(articles) {
  const counts = {};
  articles.forEach(a => {
    const day = new Date(a.date).toISOString().slice(0, 10);
    counts[day] = (counts[day] || 0) + 1;
  });
  return Object.entries(counts)
    .map(([date, count]) => ({ date, count }))
    .sort((a, b) => a.date.localeCompare(b.date));
}

export default function ArticleCharts({ articles, service }) {
  if (!articles.length) {
    return <div className="no-content">Aucune donnée à visualiser.</div>;
  }

  const time = timelineData(articles);

  return (
    <div className="charts">
      {/* Histogramme : publications par jour */}
      <div className="chart-card">
        <h3 className="chart-title">Publications par jour</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={time} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip
              contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '0.5rem' }}
              itemStyle={{ color: '#e2e8f0' }}
              labelStyle={{ color: '#9ca3af' }}
            />
            <Bar dataKey="count" fill="#06d6a0" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* PieChart : top domaines (pour RSS et Presse) */}
      {['rss', 'presse'].includes(service) && (() => {
        const byDomain = {};
        articles.forEach(a => {
          try {
            const { host } = new URL(a.url);
            byDomain[host] = (byDomain[host] || 0) + 1;
          } catch {}
        });
        
        const data = Object.entries(byDomain)
          .map(([name, value]) => ({ name, value }))
          .sort((a, b) => b.value - a.value)
          .slice(0, 8);
        
        if (data.length === 0) return null;

        return (
          <div className="chart-card">
            <h3 className="chart-title">Top 8 des domaines sources</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '0.5rem' }}
                  itemStyle={{ color: '#e2e8f0' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        );
      })()}
    </div>
  );
}