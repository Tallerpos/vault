<%*
// ── 1. BÚSQUEDA EN OPEN LIBRARY ──────────────────────
let query = tp.file.title;
if (query.startsWith("Untitled") || query === "Sin título" || query === "Libro" || query === "") {
  query = await tp.system.prompt("Título del libro o Autor");
}

if (!query) return;

const headers = { "User-Agent": "ObsidianKnowledgeVault/1.0 (contact@example.org)" };
const url = `https://openlibrary.org/search.json?q=${encodeURIComponent(query)}&language=spa&limit=20&sort=editions`;

const response = await fetch(url, { headers });
const data = await response.json();
const results = data.docs;

if (results.length === 0) {
  new Notice("No se encontró la edición en español. Procediendo manualmente.");
  var autor = await tp.system.prompt("Autor (Manual)");
  var anio = await tp.system.prompt("Año (Manual)");
  var portada = "";
  var temasExtras = [];
} else {
  const selected = await tp.system.suggester(
    (item) => {
        const t = item.title_suggest || item.title;
        const orig = item.title !== t ? ` [${item.title}]` : "";
        return `${t}${orig} (${item.author_name?.[0] || "Desconocido"}) - ${item.first_publish_year || "S.F."} [${item.edition_count || 1} ed.]`;
    },
    results,
    false,
    "Selecciona la edición correcta"
  );
  
  if (!selected) return;

  var autor = selected.author_name?.[0] || "";
  var anio = selected.first_publish_year || "";
  var portada = selected.cover_i ? `https://covers.openlibrary.org/b/id/${selected.cover_i}-M.jpg` : "";
  var temasExtras = selected.subject ? selected.subject.slice(0, 5) : [];
}
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