import React from 'react';

function resolveSource(a) {
  if (a.service)         return a.service;           // « Presse », « Reddit », …
  if (a.publisher)       return a.publisher;
  if (a.source)          return a.source;
  if (a.site)            return a.site;
  if (a.url) {
    try { return new URL(a.url).host.replace('www.', ''); }
    catch { /* ignore */ }
  }
  return 'Source inconnue';
}

function formatSource(article) {
  if (article.service && article.service.toLowerCase() === "linkedin") {
    const raw = article.source || article.publisher || article.site || "Source";
    return raw.replace(/^linkedin\s*[·\-:|.]?\s*/i, "").trim() || "Source";
  }
  return resolveSource(article);
}

export default function ArticleList({ articles }) {
  if (!articles || articles.length === 0) {
    return (
      <div className="no-articles">
        <h3>Aucun article trouvé</h3>
        <p>Essayez de modifier vos critères de recherche.</p>
      </div>
    );
  }

  return (
    <div className="articles-grid">
      {articles.map((article, index) => (
        <div key={index} className="article-card">
          <div className="article-header">
            <span className="article-source">{formatSource(article)}</span>
            <span className="article-date">
              {new Date(article.date).toLocaleDateString('fr-FR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </span>
          </div>
          
          <h3 className="article-title">
            {article.url ? (
              <a href={article.url} target="_blank" rel="noopener noreferrer">
                {article.title}
              </a>
            ) : (
              article.title
            )}
          </h3>
          
          {article.description && (
            <p className="article-description">
              {article.description.length > 150 
                ? `${article.description.substring(0, 150)}...` 
                : article.description
              }
            </p>
          )}
          
          {article.author && (
            <div className="article-author">
              Par {article.author}
            </div>
          )}
          
          <div className="article-footer">
            {article.url && (
              <a 
                href={article.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="article-link"
              >
                Lire l'article →
              </a>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}