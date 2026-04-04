<%*
// ── 1. BÚSQUEDA EN OPEN LIBRARY ──────────────────────
const query = await tp.system.prompt("Título del libro o Autor");
if (!query) return;

const response = await fetch(`https://openlibrary.org/search.json?q=${encodeURIComponent(query)}`);
const data = await response.json();
const results = data.docs.slice(0, 5); // Tomamos los 5 mejores resultados

if (results.length === 0) {
  new Notice("No se encontraron resultados. Procediendo manualmente.");
  var autor = await tp.system.prompt("Autor (Manual)");
  var anio = await tp.system.prompt("Año (Manual)");
  var portada = "";
  var temasExtras = [];
} else {
  const selected = await tp.system.suggester(
    (item) => `${item.title} (${item.author_name?.[0] || "Desconocido"}) - ${item.first_publish_year || "S.F."}`,
    results,
    false,
    "Selecciona el libro correcto"
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