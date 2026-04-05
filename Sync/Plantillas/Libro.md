<%*
// ── 1. BÚSQUEDA EN GOOGLE BOOKS ──────────────────────
let query = tp.file.title;
if (query.startsWith("Untitled") || query === "Sin título" || query === "Libro" || query === "") {
    query = await tp.system.prompt("Título (Añade el autor si es un libro muy famoso)");
}

if (!query) return;

// Filtros añadidos: 40 resultados, solo español, solo libros.
const url = `https://www.googleapis.com/books/v1/volumes?q=${encodeURIComponent(query)}&maxResults=40&langRestrict=es&printType=books`;

const response = await fetch(url);
const data = await response.json();
const results = data.items;

var titulo = query;
var autor = "";
var anio = "";
var isbn = "";
var portada = "";
var paginas = "";
var temasExtras = [];

if (!results || results.length === 0) {
    new Notice("No se encontró el libro. Procediendo manualmente.");
    autor = await tp.system.prompt("Autor (Manual)");
    anio = await tp.system.prompt("Año (Manual)");
} else {
    const selected = await tp.system.suggester(
        (item) => {
            const info = item.volumeInfo;
            const t = info.title;
            const author = info.authors ? info.authors.join(", ") : "Desconocido";
            const year = info.publishedDate ? info.publishedDate.substring(0, 4) : "S.F.";
            return `${t} (${author}) - ${year}`;
        },
        results,
        false,
        "Selecciona el libro correcto"
    );

    if (!selected) return;

    const info = selected.volumeInfo;
    
    titulo = info.title;
    autor = info.authors ? info.authors.join(", ") : "";
    anio = info.publishedDate ? info.publishedDate.substring(0, 4) : "";
    paginas = info.pageCount || "";
    temasExtras = info.categories ? info.categories : [];

    // Extraer ISBN
    if (info.industryIdentifiers) {
        let id13 = info.industryIdentifiers.find(id => id.type === "ISBN_13");
        let id10 = info.industryIdentifiers.find(id => id.type === "ISBN_10");
        isbn = id13 ? id13.identifier : (id10 ? id10.identifier : "");
    }

    // Extraer Portada en mejor resolución
    if (info.imageLinks && info.imageLinks.thumbnail) {
        portada = info.imageLinks.thumbnail.replace("http:", "https:").replace("&edge=curl", "");
    }
}

// ── 2. RENOMBRAR EL ARCHIVO SI NO TENÍA TÍTULO ────────
if (tp.file.title.startsWith("Untitled") || tp.file.title === "Sin título") {
    let safeTitle = titulo.replace(/[\\/#^[\]|:]/g, "");
    await tp.file.rename(safeTitle);
}
_%>
---
tipo: libro
autor: <% autor %>
año: <% anio %>
isbn: "<% isbn %>"
paginas: <% paginas %>
portada: "<% portada %>"
temas: <% JSON.stringify(temasExtras) %>
rating: 
estado: leyendo
---
# <% titulo %>

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