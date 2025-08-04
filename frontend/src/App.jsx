"use client";

import { useState, useEffect } from "react";
import SearchBar          from "./components/SearchBar";
import ServiceSelector    from "./components/ServiceSelector";
import ArticleList        from "./components/ArticleList";
import ArticleCharts      from "./components/ArticleCharts";
import AIReport          from "./components/AIReport";
import InsightReport      from "./components/InsightReport";
import DateRangePicker    from "./components/DateRangePicker";
import "./styles.css";

/* ─── Configuration des micro-services ─────────────────────────────────── */
export const SERVICES = [
  { value: "all",      label: "Toutes",   endpoint: null                     },
  // { value: "presse",   label: "Presse",   endpoint: "/api/presse/articles" },
  { value: "reddit",   label: "Reddit",   endpoint: "/api/reddit/articles"   },
  { value: "rss",      label: "RSS",      endpoint: "/api/rss/articles"      },
  { value: "twitter",  label: "Twitter",  endpoint: "/api/twitter/articles"  },
  { value: "youtube",  label: "YouTube",  endpoint: "/api/youtube/articles"  },
  { value: "linkedin", label: "LinkedIn", endpoint: "/api/linkedin/articles" },
];

/* ─── Composant racine ──────────────────────────────────────────────────── */
export default function App() {
  /* ••• états de recherche ••• */
  const [service,     setService]    = useState(SERVICES[0].value);
  const [query,       setQuery]      = useState("");
  const [exclude,     setExclude]    = useState("");
  const [country,     setCountry]    = useState("");   
  const [lang,        setLang]       = useState("");   
  const [start,       setStart]      = useState("");
  const [end,         setEnd]        = useState("");

  /* ••• états d’UI ••• */
  const [articles,    setArticles]   = useState([]);
  const [loading,     setLoading]    = useState(false);
  const [error,       setError]      = useState(null);
  const [activeTab,   setActiveTab]  = useState("articles");
  const [hasSearched, setHasSearched]= useState(false);
  const [aiReport, setAIReport] = useState("");
  const [reportLoading, setReportLoading] = useState(false);

  const handleDateChange = (k, v) => (k === "start" ? setStart(v) : setEnd(v));
  /* ───────────────────────────────────────────────────────────────────────
     Construit la query-string homogène pour un micro-service
  ─────────────────────────────────────────────────────────────────────── */
  const buildParams = (svcName) => {
    const p = new URLSearchParams();
    if (query.trim())   p.append("q",       query.trim());
    if (exclude.trim()) p.append("exclude", exclude.trim());
    if (country)        p.append("country", country);
    if (lang)           p.append("lang",    lang);   
    if (start)          p.append("start",   start);
    if (end)            p.append("end",     end);
    if (["reddit","twitter","youtube"].includes(svcName)) p.append("n", "1000"); 
    if (svcName === "linkedin")  p.append("n", "1000");
    return p.toString();
  };

  const POSITIVE = [
    "good", "great", "excellent", "positive", "success", "gain",
    "happy", "benefit", "favorable", "bien", "bon", "hausse"
  ];
  const NEGATIVE = [
    "bad", "poor", "terrible", "negative", "loss", "fail",
    "down", "unfavorable", "mauvais", "baisse", "crise"
  ];

  const computeStats = (arts) => {
    const stats = {
      totalMentions: arts.length,
      topSources: [],
      timeline: [],
      sentiment: { positive: 0, negative: 0, neutral: 0 }
    };

    const bySource = {};
    const byDate = {};

    arts.forEach((a) => {
      const text = `${a.title || ""} ${a.description || ""}`.toLowerCase();
      const src = (() => {
        if (a.service) return a.service;
        if (a.url) {
          try { return new URL(a.url).host; } catch { /* ignore */ }
        }
        return "Inconnu";
      })();
      bySource[src] = (bySource[src] || 0) + 1;

      const day = new Date(a.date).toISOString().slice(0, 10);
      byDate[day] = (byDate[day] || 0) + 1;

      let score = 0;
      POSITIVE.forEach((w) => text.includes(w) && score++);
      NEGATIVE.forEach((w) => text.includes(w) && score--);
      if (score > 0) stats.sentiment.positive++;
      else if (score < 0) stats.sentiment.negative++;
      else stats.sentiment.neutral++;
    });

    stats.topSources = Object.entries(bySource)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);

    stats.timeline = Object.entries(byDate)
      .map(([date, count]) => ({ date, count }))
      .sort((a, b) => a.date.localeCompare(b.date));

    return stats;
  };

  const generateReport = async (arts) => {
    const stats = computeStats(arts);
    setReportLoading(true);
    try {
      const res = await fetch("/api/ai/report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ articles: arts, stats })
      });
      if (!res.body) return;
      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop();
        for (const part of parts) {
          if (part.startsWith("data: ")) {
            const token = part.slice(6);
            if (token === "[DONE]") return;
            setAIReport((prev) => prev + token);
          }
        }
      }
    } catch {
      setAIReport({ stats });
    } finally {
      setReportLoading(false);
    }
  };

  /* ───────────────────────────────────────────────────────────────────────
     Récupère les articles (un seul service ou “all”)
  ─────────────────────────────────────────────────────────────────────── */
  const fetchArticles = async () => {
    setLoading(true);
    setAIReport("");
    setError(null);
    setHasSearched(true);

    const fetchOne = async (svc) => {
      if (!svc.endpoint) return [];
      const qs  = buildParams(svc.value);
      const url = qs ? `${svc.endpoint}?${qs}` : svc.endpoint;
      const res = await fetch(url);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || `Erreur ${svc.label}`);
      const arr = Array.isArray(data) ? data : data.articles || [];
      return arr.map((item) => ({ ...item, service: svc.label }));
    };

    try {
      let collected = [];
      if (service === "all") {
        const results = await Promise.allSettled(
          SERVICES.filter((s) => s.endpoint).map(fetchOne)
        );
        results.forEach((r) => r.status === "fulfilled" && (collected = collected.concat(r.value)));
      } else {
        const svc = SERVICES.find((s) => s.value === service);
        collected = await fetchOne(svc);
      }
      generateReport(collected);
      setArticles(collected);
    } catch (e) {
      setError(e.message);
      setArticles([]);
    } finally {
      setLoading(false);
    }
  };

  // Trigger new search when language or country changes after first search
  useEffect(() => {
    if (hasSearched) {
      fetchArticles();
    }
  }, [lang, country]);

  /* ───────────────────────────────────────────────────────────────────────
     Filtrage date côté client (sécurité)
  ─────────────────────────────────────────────────────────────────────── */
  const filtered = articles.filter((a) => {
    const d = new Date(a.date);
    if (start && d < new Date(start)) return false;
    if (end   && d > new Date(end + "T23:59:59")) return false;
    if (lang && a.langue && a.langue.toLowerCase() !== lang.toLowerCase()) return false;
    if (country && a.country && a.country.toLowerCase() !== country.toLowerCase()) return false;
    return true;
  });

  /* ───────────────────────────────────────────────────────────────────────
     Rendu
  ─────────────────────────────────────────────────────────────────────── */
  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="app-title">MCTN ComTracker</h1>

        {/* --- BARRE DE RECHERCHE + CONTRÔLES --- */}
        <SearchBar
          query={query}              onChange={setQuery}
          exclude={exclude}          onExcludeChange={setExclude}
          country={country}          onCountryChange={setCountry}   /* ← NEW */
          lang={lang}                onLangChange={setLang}         /* ← NEW */
          onSearch={fetchArticles}
        />

        <div className="controls-section">
          <ServiceSelector
            services={SERVICES}
            service={service}
            onChange={setService}
          />
          <DateRangePicker
            start={start}
            end={end}
            onChange={handleDateChange}
          />

          {/* NEW LANGUAGE FILTER INPUT */}
          <div className="filter-group">
            <label>Langue :</label>
            <input
              type="text"
              value={lang}
              onChange={(e) => setLang(e.target.value.toLowerCase())}
              placeholder="fr, en, es…"
              className="filter-input"
            />
          </div>

          {/* NEW COUNTRY FILTER INPUT */}
          <div className="filter-group">
            <label>Pays :</label>
            <input
              type="text"
              value={country}
              onChange={(e) => setCountry(e.target.value.toLowerCase())}
              placeholder="sn, fr, us…"
              className="filter-input"
            />
          </div>
        </div>

        {hasSearched && (
          <div className="tabs-container">
            <button className={`tab ${activeTab==="articles"?'active':''}`} onClick={()=>setActiveTab("articles")}>
              Articles ({filtered.length})
            </button>
            <button className={`tab ${activeTab==="visualisations"?'active':''}`} onClick={()=>setActiveTab("visualisations")}>Visualisations</button>
            <button className={`tab ${activeTab==="rapport"?'active':''}`} onClick={()=>setActiveTab("rapport")}>Rapport</button>
          </div>
        )}
      </header>

      {/* OVERLAY de chargement */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <p className="loading-message">Chargement des articles…</p>
        </div>
      )}

      {/* CONTENU PRINCIPAL */}
      <main className="app-main">
        {!hasSearched && (
          <div className="welcome-message">
            <h2>Bienvenue sur MCTN ComTracker</h2>
            <p>Recherchez des articles à travers différentes sources.</p>
            <div className="features">
              <div className="feature">📰 Articles de presse</div>
              <div className="feature">🔍 Recherche Reddit</div>
              <div className="feature">📡 Flux RSS</div>
              <div className="feature">🐦 Posts Twitter</div>
              <div className="feature">📺 Vidéos YouTube</div>
              <div className="feature">💼 LinkedIn posts</div>
            </div>
          </div>
        )}

        {hasSearched && activeTab==="articles" && !loading && (
          error ? (
            <p className="error-message">{error}</p>
          ) : (
            <>
              {reportLoading
                ? <p className="loading-report">loading report...</p>
                : <AIReport text={aiReport} />}
              <ArticleList articles={filtered} />
            </>
          )
        )}

        {hasSearched && activeTab==="visualisations" && (
          <ArticleCharts articles={filtered} service={service} />
        )}

        {hasSearched && activeTab==="rapport" && (
          <>
            <InsightReport articles={filtered} />
            <AIReport
                summary={aiReport.summary}
                sentiment={aiReport.sentiment}
                stats={aiReport.stats}
              />
          </>
        )}
      </main>
    </div>
  );
}