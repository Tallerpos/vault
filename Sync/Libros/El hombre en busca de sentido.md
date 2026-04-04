<%*
// ── 1. PREPARACIÓN DE BÚSQUEDA ──────────────────────
// Si el archivo ya tiene un nombre (Templater/QuickAdd), lo usamos para buscar
let query = tp.file.title;
if (query.startsWith("Untitled") || query === "Sin título" || query === "Libro") {
  query = await tp.system.prompt("Título del libro o Autor");
}

if (!query) return;

const response = await fetch(`https://openlibrary.org/search.json?q=${encodeURIComponent(query)}`);
const data = await response.json();
const results = data.docs.slice(0, 10); // Más resultados para mayor precisión

if (results.length === 0) {
  new Notice("Exacto no encontrado. Procediendo manualmente.");
  var autor = await tp.system.prompt("Autor (Manual)");
  var anio = await tp.system.prompt("Año (Manual)");
  var portada = "";
  var temasExtras = [];
} else {
  const selected = await tp.system.suggester(
    (item) => `${item.title} (${item.author_name?.[0] || "Desconocido"}) - ${item.first_publish_year || "S.F."} ${item.isbn?.[0] ? "["+item.isbn[0]+"]" : ""}`,
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