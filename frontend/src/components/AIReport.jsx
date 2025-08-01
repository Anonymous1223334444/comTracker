import React from "react";

export default function AIReport({ summary, sentiment }) {
  if (!summary && !sentiment) {
    return <p className="no-content">Aucun rapport disponible.</p>;
  }
  return (
    <div className="ai-report">
      {summary && <p className="report-summary">{summary}</p>}
      {sentiment && <p className="report-sentiment">Sentiment&nbsp;: {sentiment}</p>}
    </div>
  );
}