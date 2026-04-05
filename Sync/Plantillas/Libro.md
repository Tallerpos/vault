<%*
// ── 1. BÚSQUEDA EN OPEN LIBRARY ──────────────────────
let query = tp.file.title;
if (query.startsWith("Untitled") || query === "Sin título" || query === "Libro" || query === "") {
    query = await tp.system.prompt("Título del libro o Autor");
}

if (!query) return;

const headers = { "User-Agent": "ObsidianKnowledgeVault/1.0" };

// CORRECCIÓN CLAVE: Se eliminó '&sort=editions' para que ordene por relevancia exacta.
// Ahora si buscas "El hombre en busca de sentido", priorizará esa frase exacta.
const url = `https://openlibrary.org/search.json?q=${encodeURIComponent(query)}&limit=15`;

const response = await fetch(url, { headers });
const data = await response.json();
const results = data.docs;

var autor = "";
var anio = "";
var isbn = "";
var portada = "";
var temasExtras = [];

if (results.length === 0) {
    new Notice("No se encontró el libro. Procediendo manualmente.");
    autor = await tp.system.prompt("Autor (Manual)");
    anio = await tp.system.prompt("Año (Manual)");
} else {
    const selected = await tp.system.suggester(
        (item) => {
            const t = item.title;
            const author = item.author_name ? item.author_name[0] : "Desconocido";
            const year = item.first_publish_year || "S.F.";
            const editions = item.edition_count || 1;
            return `${t} (${author}) - ${year} [${editions} ed.]`;
        },
        results,
        false,
        "Selecciona el libro correcto"
    );

    if (!selected) return;

    autor = selected.author_name ? selected.author_name[0] : "";
    anio = selected.first_publish_year || "";
    isbn = selected.isbn ? selected.isbn[0] : "";
    portada = selected.cover_i ? `https://covers.openlibrary.org/b/id/${selected.cover_i}-L.jpg` : "";
    temasExtras = selected.subject ? selected.subject.slice(0, 5) : [];
}
_%>
---
tipo: libro
autor: <% autor %>
año: <% anio %>
isbn: "<% isbn %>"
portada: "<% portada %>"
temas: <% JSON.stringify(temasExtras) %>
rating: 
estado: leyendo
---
# <% tp.file.title === "Untitled" || tp.file.title === "Sin título" ? query : tp.file.title %>

![Portada|<% portada %>]

## Por qué lo leí


## Tesis


## Notas brutas


## Ideas generadas

```dataview
LIST
FROM "ideas"
WHERE contains(file.outlinks, this.file.link)
SORT file.ctime ASC
```