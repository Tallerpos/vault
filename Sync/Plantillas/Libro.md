<%*
// ── 1. BÚSQUEDA MULTI-MOTOR (V11.0) ──────────────────
let query = tp.file.title;
if (query.startsWith("Untitled") || query === "Sin título" || query === "Libro" || query === "") {
  query = await tp.system.prompt("Título, Autor o ISBN");
}

if (!query) return;

const isISBN = /^(97(8|9))?\d{9}(\d|X)$/.test(query.replace(/-/g, ""));
const searchType = isISBN ? `isbn:${query}` : query;

let results = [];
let errorOccurred = false;

// --- FUNCION DE BUSQUEDA (Google Books) ---
async function searchGoogleBooks(q) {
  const url = `https://www.googleapis.com/books/v1/volumes?q=${encodeURIComponent(q)}&maxResults=10`;
  try {
    const response = await requestUrl({ url: url });
    return response.json.items || [];
  } catch (e) {
    console.error("Google Books Error:", e);
    return [];
  }
}

// --- FUNCION DE BUSQUEDA (Open Library Fallback) ---
async function searchOpenLibrary(q) {
  const url = `https://openlibrary.org/search.json?q=${encodeURIComponent(q)}&limit=10`;
  try {
    const response = await requestUrl({ url: url });
    return response.json.docs || [];
  } catch (e) {
    console.error("Open Library Error:", e);
    return [];
  }
}

// ── EJECUCIÓN DE BÚSQUEDA ────────────────────────────
new Notice("Buscando libro...");
results = await searchGoogleBooks(searchType);

// Si Google Books falla, intentamos con Open Library
if (results.length === 0) {
  new Notice("Google Books no respondió, intentando motor alternativo...");
  const olResults = await searchOpenLibrary(searchType);
  if (olResults.length > 0) {
    results = olResults.map(item => ({
      volumeInfo: {
        title: item.title,
        authors: item.author_name,
        publishedDate: item.first_publish_year ? String(item.first_publish_year) : "",
        imageLinks: item.cover_i ? { thumbnail: `https://covers.openlibrary.org/b/id/${item.cover_i}-M.jpg` } : null,
        industryIdentifiers: item.isbn ? [{ identifier: item.isbn[0] }] : []
      }
    }));
  }
}

// ── PROCESAMIENTO DE SELECCIÓN ────────────────────────
if (results.length === 0) {
  new Notice("No se encontró el libro automáticamente.");
  var autor = await tp.system.prompt("Autor (Manual)");
  var anio = await tp.system.prompt("Año (Manual)");
  var isbn = isISBN ? query : "";
  var portada = "";
  var temasExtras = [];
} else {
  const selected = await tp.system.suggester(
    (item) => `${item.volumeInfo.title} (${item.volumeInfo.authors?.[0] || "Desconocido"}) - ${item.volumeInfo.publishedDate || "S.F."}`,
    results,
    false,
    "Selecciona el libro correcto"
  );
  
  if (!selected) return;

  const info = selected.volumeInfo;
  var autor = info.authors?.[0] || "";
  var anio = String(info.publishedDate || "").split("-")[0];
  var isbn = info.industryIdentifiers?.find(id => id.type.includes("ISBN"))?.identifier || info.industryIdentifiers?.[0]?.identifier || "";
  var portada = info.imageLinks?.thumbnail ? info.imageLinks.thumbnail.replace("http://", "https://") : "";
  var temasExtras = info.categories || [];
}
_%>
---
tipo: libro
autor: <% autor %>
año: <% anio %>
isbn: <% isbn %>
portada: "<% portada %>"
temas: <% JSON.stringify(temasExtras) %>
rating: 
estado: leyendo
---

```dataviewjs
const p = dv.current();
const u_open = "\u005B\u005B";
const u_close = "\u005D\u005D";

// 1. Estadísticas automáticas
const ideasCount = dv.pages('"ideas"').filter(i => {
    return i.fuente && String(i.fuente).includes(p.file.name);
}).length;

// 2. Render de Cabecera Elite (Resiliente)
const container = this.container.createDiv({ style: "display: flex; flex-wrap: wrap; gap: 30px; padding: 25px; background: var(--background-secondary-alt); border-radius: 15px; border: 1px solid var(--divider-color); margin-bottom: 30px; min-height: 250px;" });

const imgCol = container.createDiv({ style: "width: 180px; min-width: 150px; flex: 0 0 180px; height: 270px; border-radius: 8px; overflow: hidden; box-shadow: 0 10px 20px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; position: relative;" });

if (p.portada && p.portada !== "") {
    imgCol.createEl("img", { attr: { src: p.portada }, style: "width: 100%; height: 100%; object-fit: cover;" });
} else {
    imgCol.style.background = "linear-gradient(135deg, var(--interactive-accent) 0%, var(--background-modifier-border) 100%)";
    imgCol.createDiv({ text: p.file.name, style: "padding: 20px; color: white; font-weight: 700; text-align: center; font-size: 1.1em; line-height: 1.3;" });
}

const infoCol = container.createDiv({ style: "flex: 1; min-width: 250px; display: flex; flex-direction: column; justify-content: flex-start;" });
const topInfo = infoCol.createDiv();
topInfo.createEl("h1", { text: p.file.name, style: "margin: 0 0 5px 0; border: none; font-size: 1.8em; line-height: 1.2; font-weight: 800;" });
topInfo.createEl("div", { text: p.autor || "Autor Desconocido", style: "font-size: 1.2em; color: var(--text-muted); font-weight: 500; margin-bottom: 20px;" });

const statsRow = infoCol.createDiv({ style: "display: flex; flex-wrap: wrap; gap: 12px; align-items: center; margin-top: auto;" });
const estadoBadge = statsRow.createDiv({ style: "padding: 6px 15px; border-radius: 6px; font-size: 0.75em; font-weight: 700; letter-spacing: 1px; background: var(--interactive-accent); color: white;" });
estadoBadge.innerText = (p.estado || "Pendiente").toUpperCase();

const countBadge = statsRow.createDiv({ style: "padding: 6px 15px; border-radius: 6px; font-size: 0.75em; font-weight: 600; background: var(--background-primary); border: 1px solid var(--divider-color); color: var(--text-normal);" });
countBadge.innerHTML = `CONEXIONES: <b>${ideasCount}</b>`;

if (p.rating) {
    const ratingRow = infoCol.createDiv({ style: "margin-top: 15px; font-size: 1.3em; color: var(--interactive-accent); letter-spacing: 3px;" });
    ratingRow.innerText = "★".repeat(p.rating) + "☆".repeat(5 - p.rating);
}
```

## Por qué lo leí

## Tesis

## Notas brutas
(Escribe aquí las ideas que surjan de la lectura)

---

## Ideas vinculadas
```dataview
LIST
FROM "ideas"
WHERE contains(file.outlinks, this.file.link) OR contains(fuente, this.file.name)
SORT file.mtime DESC
```