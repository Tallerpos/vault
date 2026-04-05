<%*
// ── 1. CONFIGURACIÓN E IDENTIFICACIÓN ─────────────────────────────────────────
let query = tp.file.title;
const titulosGenericos = ["Untitled", "Sin título", "Libro", "New note", ""];
const esGenerico = titulosGenericos.some(t => query.startsWith(t) || query === "");

if (esGenerico) {
    query = await tp.system.prompt("Título del libro (añade el autor para precisión)");
    if (!query) { new Notice("Cancelado."); return; }
}

// ── 2. BÚSQUEDA INTERACTIVA (GOOGLE BOOKS) ────────────────────────────────────
let selected = null;
let manualMode = false;

while (!selected && !manualMode) {
    const url = `https://www.googleapis.com/books/v1/volumes?q=${encodeURIComponent(query)}&maxResults=20&langRestrict=es&printType=books`;
    let results = [];
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        results = data.items || [];
    } catch(e) {
        new Notice("Error de red. Pasando a modo manual.");
        manualMode = true;
        break;
    }

    // Preparar opciones del buscador
    const options = results.map(item => {
        const info = item.volumeInfo;
        const t = info.title || "Sin título";
        const author = info.authors ? info.authors.join(", ") : "Desconocido";
        const year = info.publishedDate ? info.publishedDate.substring(0, 4) : "S.F.";
        return { 
            display: `📖 ${t} · ${author} (${year})`, 
            value: item,
            type: "book"
        };
    });

    // Añadir opciones de control
    options.push({ display: "🔍 Buscar otro título...", value: null, type: "search" });
    options.push({ display: "✏️ Rellenar manualmente...", value: null, type: "manual" });

    const choice = await tp.system.suggester(item => item.display, options, false, `Resultados para: "${query}"`);

    if (!choice) { // Cancelado con ESC
        new Notice("Cancelado."); return;
    } else if (choice.type === "book") {
        selected = choice.value;
    } else if (choice.type === "search") {
        query = await tp.system.prompt("Nuevo título a buscar", query);
        if (!query) return;
    } else if (choice.type === "manual") {
        manualMode = true;
    }
}

// ── 3. EXTRACCIÓN DE DATOS ────────────────────────────────────────────────────
let titulo = query, autor = "", anio = "", isbn = "", portada = "", paginas = "", idioma = "", editorial = "", sinopsis = "", temasExtras = [];
const fechaInicio = tp.date.now("YYYY-MM-DD");

if (selected) {
    const info = selected.volumeInfo;
    titulo = info.title || query;
    autor = info.authors ? info.authors.join(", ") : "";
    anio = info.publishedDate ? info.publishedDate.substring(0, 4) : "";
    paginas = info.pageCount ? String(info.pageCount) : "";
    editorial = info.publisher || "";
    idioma = info.language ? info.language.toUpperCase() : "";
    temasExtras = info.categories || [];

    if (info.description) {
        sinopsis = info.description.replace(/(<([^>]+)>)/gi, "").replace(/\s+/g, " ").trim().substring(0, 500);
        if (info.description.length > 500) sinopsis += "…";
    }

    if (info.industryIdentifiers) {
        const id13 = info.industryIdentifiers.find(id => id.type === "ISBN_13");
        isbn = id13 ? id13.identifier : (info.industryIdentifiers[0]?.identifier || "");
    }

    if (info.imageLinks) {
        const base = info.imageLinks.extraLarge || info.imageLinks.large || info.imageLinks.medium || info.imageLinks.thumbnail || "";
        portada = base.replace("http:", "https:").replace("&edge=curl", "").replace(/zoom=\d/, "fife=w400");
    }
} else if (manualMode) {
    titulo = await tp.system.prompt("Título", query) || query;
    autor = await tp.system.prompt("Autor") || "";
    anio = await tp.system.prompt("Año") || "";
}

// Fallback Portada
if (!portada && isbn) {
    portada = `https://covers.openlibrary.org/b/isbn/${isbn}-L.jpg`;
}

// ── 4. RENOMBRAR ARCHIVO ──────────────────────────────────────────────────────
if (esGenerico) {
    const safeTitle = titulo.replace(/[\\/#^[\]|:?]/g, "").trim();
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