<%*
// ── 1. BúSQUEDA EN OPEN LIBRARY ──────────────────────
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
  var isbn = "";
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
  var isbn = selected.isbn ? selected.isbn[0] : "";
  var portada = selected.cover_i ? `https://covers.openlibrary.org/b/id/${selected.cover_i}-L.jpg` : "";
  var temasExtras = selected.subject ? selected.subject.slice(0, 5) : [];
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

// 2. Render de Cabecera Elite
const container = this.container.createDiv({ style: "display: flex; flex-wrap: wrap; gap: 30px; padding: 25px; background: var(--background-secondary-alt); border-radius: 15px; border: 1px solid var(--divider-color); margin-bottom: 30px;" });

// Columna Imagen
const imgCol = container.createDiv({ style: "width: 180px; min-width: 150px; flex: 0 0 180px;" });
const img = imgCol.createEl("img", { attr: { src: p.portada || "https://via.placeholder.com/180x270?text=Sin+Portada" } });
img.style.width = "100%";
img.style.borderRadius = "8px";
img.style.boxShadow = "0 10px 20px rgba(0,0,0,0.3)";

// Columna Info
const infoCol = container.createDiv({ style: "flex: 1; min-width: 250px; display: flex; flex-direction: column; justify-content: space-between;" });

// Titulo y Autor
const topInfo = infoCol.createDiv();
topInfo.createEl("h1", { text: p.file.name, style: "margin: 0 0 5px 0; border: none; font-size: 1.8em; line-height: 1.2;" });
topInfo.createEl("div", { text: p.autor || "Autor Desconocido", style: "font-size: 1.1em; color: var(--text-muted); font-weight: 500;" });

// Stats y Badges
const statsRow = infoCol.createDiv({ style: "display: flex; gap: 20px; align-items: center; margin-top: 15px;" });

// Badge de Estado
const estadoBadge = statsRow.createDiv({ style: "padding: 5px 12px; border-radius: 20px; font-size: 0.8em; font-weight: 700; text-transform: uppercase; background: var(--interactive-accent); color: white;" });
estadoBadge.innerText = (p.estado || "Pendiente").toUpperCase();

// Ideas generadas
const ideasStat = statsRow.createDiv({ style: "font-size: 0.9em; color: var(--text-normal);" });
ideasStat.innerHTML = `<b>${ideasCount}</b> Ideas generadas`;

// Rating visual
if (p.rating) {
    const ratingRow = infoCol.createDiv({ style: "margin-top: 10px; font-size: 1.1em; color: var(--interactive-accent);" });
    ratingRow.innerText = "★".repeat(p.rating) + "☆".repeat(5 - p.rating);
}
```

## Por qué lo leí

## Tesis

## Notas brutas
(Escribe aquí tus ideas principales y las iremos convirtiendo en notas independientes)

---

## Ideas Generativas vinculadas
```dataview
LIST
FROM "ideas"
WHERE contains(file.outlinks, this.file.link) OR contains(fuente, this.file.name)
SORT file.mtime DESC
```