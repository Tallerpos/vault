<%*
// ── 1. BÚSQUEDA EN GOOGLE BOOKS ──────────────────────────────────────────────
const API_KEY = "AIzaSyChJ0JOuVdZ55PCj0dLoXGYcYZ2LT7_Vso";
let query = tp.file.title;
const titulosGenericos = ["Untitled", "Sin título", "Libro", "New note", ""];

if (titulosGenericos.some(t => tp.file.title.startsWith(t) || tp.file.title === t)) {
    query = await tp.system.prompt("Título del libro");
}

if (!query || query.trim() === "") { new Notice("Cancelado."); return; }

const url = `https://www.googleapis.com/books/v1/volumes?q=${encodeURIComponent(query)}&maxResults=40&printType=books&orderBy=relevance&key=${API_KEY}`;
let results = [];

try {
    // Usamos requestUrl (API de Obsidian) para evitar bloqueos de CORS y mayor robustez
    const response = await requestUrl({ url: url });
    const data = response.json;
    results = data.items || [];
} catch(e) {
    if (e.status === 429) {
        new Notice("Exceso de peticiones (Rate Limit). Espera un momento.");
    } else {
        new Notice("Error en la búsqueda. Revisa tu conexión o la API Key.");
    }
    console.error("Google Books Error:", e);
}

// ── 2. VARIABLES BASE ─────────────────────────────────────────────────────────
var titulo      = query;
var autor       = "";
var anio        = "";
var isbn        = "";
var portada     = "";
var paginas     = "";
var idioma      = "";
var editorial   = "";
var sinopsis    = "";
var temasExtras = [];
var fechaInicio = tp.date.now("YYYY-MM-DD");

// ── 3. SELECCIÓN O MODO MANUAL ────────────────────────────────────────────────
if (!results || results.length === 0) {
    new Notice("Sin resultados. Rellena los datos manualmente.");
    titulo    = await tp.system.prompt("Título") || query;
    autor     = await tp.system.prompt("Autor") || "";
    anio      = await tp.system.prompt("Año") || "";
    editorial = await tp.system.prompt("Editorial") || "";
    paginas   = await tp.system.prompt("Número de páginas") || "";
} else {
    const selected = await tp.system.suggester(
        (item) => {
            const info   = item.volumeInfo;
            const t      = info.title || "Sin título";
            const author = info.authors ? info.authors.join(", ") : "Desconocido";
            const year   = info.publishedDate ? info.publishedDate.substring(0, 4) : "S.F.";
            const lang   = info.language ? ` [${info.language.toUpperCase()}]` : "";
            return `${t} · ${author} · ${year}${lang}`;
        },
        results,
        false,
        "Selecciona el libro correcto (ESC = manual)"
    );

    if (!selected) {
        new Notice("Selección cancelada. Rellena los datos manualmente.");
        titulo    = await tp.system.prompt("Título") || query;
        autor     = await tp.system.prompt("Autor") || "";
        anio      = await tp.system.prompt("Año") || "";
        editorial = await tp.system.prompt("Editorial") || "";
        paginas   = await tp.system.prompt("Número de páginas") || "";
    } else {
        const info = selected.volumeInfo;

        titulo      = info.title         || query;
        autor       = info.authors       ? info.authors.join(", ")             : "";
        anio        = info.publishedDate ? info.publishedDate.substring(0, 4)  : "";
        paginas     = info.pageCount     ? String(info.pageCount)              : "";
        editorial   = info.publisher     || "";
        idioma      = info.language      ? info.language.toUpperCase()         : "";
        temasExtras = info.categories    || [];

        // Sinopsis: limpia HTML y recorta a 500 caracteres
        if (info.description) {
            sinopsis = info.description
                .replace(/(<([^>]+)>)/gi, "")
                .replace(/\s+/g, " ")
                .trim()
                .substring(0, 500);
            if (info.description.length > 500) sinopsis += "…";
        }

        // ISBN (preferir ISBN-13)
        if (info.industryIdentifiers) {
            const id13 = info.industryIdentifiers.find(id => id.type === "ISBN_13");
            const id10 = info.industryIdentifiers.find(id => id.type === "ISBN_10");
            isbn = id13 ? id13.identifier : (id10 ? id10.identifier : "");
        }

        // Portada — fife=w400 funciona sin bloqueo de referrer
        if (info.imageLinks) {
            const base = info.imageLinks.extraLarge
                      || info.imageLinks.large
                      || info.imageLinks.medium
                      || info.imageLinks.thumbnail
                      || "";
            portada = base
                .replace("http:", "https:")
                .replace("&edge=curl", "")
                .replace(/zoom=\d/, "fife=w400");
        }

        // Fallback: Open Library por ISBN (sin bloqueo de referrer)
        if (!portada && isbn) {
            portada = `https://covers.openlibrary.org/b/isbn/${isbn}-L.jpg`;
        }
    }
}

// ── 4. RENOMBRAR ARCHIVO ──────────────────────────────────────────────────────
if (titulosGenericos.some(t => tp.file.title.startsWith(t) || tp.file.title === t)) {
    const safeTitle = titulo.replace(/[\\/#^[\]|:]/g, "").trim();
    await tp.file.rename(safeTitle);
}
_%>
---
tipo: libro
titulo: "<% titulo %>"
autor: "<% autor %>"
año: <% anio %>
editorial: "<% editorial %>"
idioma: "<% idioma %>"
isbn: "<% isbn %>"
paginas: <% paginas %>
pagina_actual: 0
portada: "<% portada %>"
temas: <% JSON.stringify(temasExtras) %>
rating: 
estado: leyendo
fecha_inicio: <% fechaInicio %>
fecha_fin: 
---

<% portada ? `![${titulo}|200](${portada})` : "_Sin portada disponible_" %>

# <% titulo %>
**<% autor %>** · <% anio %><% editorial ? ` · ${editorial}` : "" %>

<% sinopsis ? `> ${sinopsis}` : "" %>

---

## Por qué lo leí


## Tesis principal


## Notas brutas


## Ideas clave
```dataview
LIST
FROM "ideas"
WHERE contains(fuente, this.file.name)
SORT file.ctime ASC
```

## Resumen final


## Rating y veredicto