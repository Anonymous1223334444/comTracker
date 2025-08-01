import React from "react";

export default function SearchBar({
  /* champs & callbacks provenant de App.jsx */
  query,          onChange,
  exclude,        onExcludeChange,
  country,        onCountryChange,
  lang,           onLangChange,
  onSearch,
}) {
  /* déclenche la recherche au “Enter” seulement si un mot-clé est présent */
  const handleKeyDown = (e) =>
    e.key === "Enter" && query.trim() && onSearch();

  /* listes déroulantes */
  const COUNTRIES = [
    { value: "",    label: "Tous pays" },
    { value: "INTL",label: "International (.com)" },
    { value: "SN",  label: "Sénégal"  },
    { value: "FR",  label: "France"   },
    { value: "US",  label: "USA"      },
    { value: "GB",  label: "R-Uni"    },
    { value: "CM",  label: "Cameroun" },
  ];


  const LANGS = [
    { value: "",  label: "Toutes langues" },
    { value: "fr", label: "Français"      },
    { value: "en", label: "English"       },
    { value: "es", label: "Español"       },
    { value: "pt", label: "Português"     },
  ];

  const disabled = !query.trim();          // bouton grisé si champ vide

  return (
    <div className="search-container">
      <div className="search-inputs">
        {/* Mot-clé ------------------------------------------------------- */}
        <div className="input-group">
          <input
            type="text"
            placeholder="Rechercher…"
            value={query}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            className="search-input primary-input"
          />
          <span className="input-icon">🔍</span>
        </div>

        {/* Exclusion ----------------------------------------------------- */}
        <div className="input-group">
          <input
            type="text"
            placeholder="Exclure (mots ou ,)"
            value={exclude}
            onChange={(e) => onExcludeChange(e.target.value)}
            onKeyDown={handleKeyDown}
            className="search-input exclude-input"
          />
          <span className="input-icon">🚫</span>
        </div>

        {/* Pays ---------------------------------------------------------- */}
        <div className="input-group">
          <select
            value={country}
            onChange={(e) => onCountryChange(e.target.value)}
            className="search-select"
          >
            {COUNTRIES.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>
        </div>

        {/* Langue -------------------------------------------------------- */}
        <div className="input-group">
          <select
            value={lang}
            onChange={(e) => onLangChange(e.target.value)}
            className="search-select"
          >
            {LANGS.map((l) => (
              <option key={l.value} value={l.value}>
                {l.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Bouton Recherche ------------------------------------------------ */}
      <button
        onClick={onSearch}
        className="search-button"
        disabled={disabled}
        title={disabled ? "Entrez un mot-clé" : "Lancer la recherche"}
      >
        Rechercher
      </button>
    </div>
  );
}
