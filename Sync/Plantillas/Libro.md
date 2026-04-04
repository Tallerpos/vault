<%*
// ── 1. PREPARACIÓN DE BÚSQUEDA ──────────────────────
// Usamos el título del archivo o pedimos uno si es genérico
let query = tp.file.title;
if (query.startsWith("Untitled") || query === "Sin título" || query === "Libro" || query === "") {
  query = await tp.system.prompt("Título del libro o Autor");
}

if (!query) return;

// Según documentación: Identificarse mejora el límite de peticiones
const headers = {
  "User-Agent": "ObsidianKnowledgeVault/1.0 (contact@example.org)"
};

// q: búsqueda general, limit: 20 resultados, sort: editions (prioriza obras principales)
const url = `https://openlibrary.org/search.json?q=${encodeURIComponent(query)}&limit=20&sort=editions`;

const response = await fetch(url, { headers });
const data = await response.json();
const results = data.docs;

if (results.length === 0) {
  new Notice("No se encontraron resultados en Open Library.");
  var autor = await tp.system.prompt("Autor (Manual)");
  var anio = await tp.system.prompt("Año (Manual)");
  var portada = "";
  var temasExtras = [];
} else {
  const selected = await tp.system.suggester(
    (item) => `${item.title} (${item.author_name?.[0] || "Desconocido"}) - ${item.first_publish_year || "S.F."} [${item.edition_count || 1} ediciones]`,
    results,
    false,
    "Selecciona la edición correcta (Las primeras suelen ser las principales)"
  );
  
  if (!selected) return;

  var autor = selected.author_name?.[0] || "";
  var anio = selected.first_publish_year || "";
  var portada = selected.cover_i ? `https://covers.openlibrary.org/b/id/${selected.cover_i}-M.jpg` : "";
  var temasExtras = selected.subject ? selected.subject.slice(0, 5) : [];
}

// ── 2. PREPARACIÓN DE FRONTMATTER ───────────────────
_%>
---
tipo: libro
autor: <% autor %>
año: <% anio %>
portada: "<% portada %>"
temas: <% JSON.stringify(temasExtras) %>
rating: 
estado: leyendo
---

# <% tp.file.title %>

![Portada|<% portada %>]

## Por qué lo leí

## Tesis

## Notas brutas

---

## Ideas generadas
```dataview
LIST
FROM "ideas"
WHERE contains(file.outlinks, this.file.link)
SORT file.ctime ASC
```