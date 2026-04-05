# Dashboard de Lectura
> [!NOTE]
> Versión 3.1: Si no ves este título en español, por favor cierra y vuelve a abrir la nota para forzar la sincronización de archivos.

## Biblioteca Visual (Galería)
```dataviewjs
// 1. Inyección de Estilos Ultra-Robustos
const styles = `
.dashboard-grid {
    display: grid !important;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)) !important;
    gap: 30px !important;
    padding: 24px 0 !important;
    width: 100% !important;
}
.book-card {
    background: var(--background-secondary-alt) !important;
    border-radius: 14px !important;
    overflow: hidden !important;
    transition: transform 0.3s ease, box-shadow 0.3s ease !important;
    border: 1px solid var(--divider-color) !important;
    display: flex !important;
    flex-direction: column !important;
    text-decoration: none !important;
}
.book-card:hover {
    transform: translateY(-8px) !important;
    box-shadow: 0 15px 30px rgba(0,0,0,0.3) !important;
    border-color: var(--interactive-accent) !important;
}
.book-cover-container {
    width: 100% !important;
    aspect-ratio: 2 / 3 !important;
    background: var(--background-primary) !important;
}
.book-cover {
    width: 100% !important;
    height: 100% !important;
    object-fit: cover !important;
}
.book-info {
    padding: 15px !important;
    background: var(--background-secondary) !important;
    flex-grow: 1 !important;
}
.book-title {
    font-weight: 700 !important;
    font-size: 0.95em !important;
    margin-bottom: 5px !important;
    color: var(--text-normal) !important;
}
.book-author {
    font-size: 0.85em !important;
    color: var(--text-muted) !important;
}
.book-rating {
    margin-top: 10px !important;
    font-size: 0.8em !important;
    color: var(--text-accent) !important;
    font-weight: 600 !important;
}
`;
dv.el("style", styles);

// 2. Obtener Libros Ordenados
const books = dv.pages('"Libros"')
    .where(p => p.tipo === "libro")
    .sort(p => p.rating, "desc")
    .sort(p => p.file.mtime, "desc");

if (books.length === 0) {
    dv.paragraph("No se detectaron libros. Verifica que los archivos en la carpeta 'Libros' tengan 'tipo: libro' en su configuración inicial.");
} else {
    // 3. Renderizado del Grid
    let html = '<div class="dashboard-grid">';
    for (const book of books) {
        const cover = book.portada || "https://via.placeholder.com/180x270?text=Sin+Portada";
        const ratingText = book.rating ? "Puntuación: " + book.rating + "/5" : "Pendiente de calificar";
        html += `
            <a href="${book.file.path}" class="internal-link book-card">
                <div class="book-cover-container">
                    <img src="${cover}" class="book-cover">
                </div>
                <div class="book-info">
                    <div class="book-title">${book.file.name}</div>
                    <div class="book-author">${book.autor || "Desconocido"}</div>
                    <div class="book-rating">${ratingText}</div>
                </div>
            </a>
        `;
    }
    html += '</div>';
    dv.el("div", html);
}
```

---

## Ideas por Temas
```dataviewjs
const ideas = dv.pages('"ideas"').where(p => p.tipo === "idea");
const temaMap = new Map();

for (const idea of ideas) {
  const temas = idea.temas
    ? (Array.isArray(idea.temas) ? idea.temas : [idea.temas])
    : ["Sin clasificar"];
  for (const tema of temas) {
    if (!temaMap.has(tema)) temaMap.set(tema, []);
    temaMap.get(tema).push(idea);
  }
}

if (temaMap.size === 0) {
  dv.paragraph("Aún no has generado ideas. Usa la plantilla para empezar.");
} else {
  for (const [tema, notas] of [...temaMap.entries()].sort()) {
    dv.header(3, `${tema} (${notas.length})`);
    dv.list(notas.map(n => n.file.link));
  }
}
```

---

## Actividad Reciente
```dataview
TABLE fuente as "Origen", temas as "Temas"
FROM "ideas"
WHERE tipo = "idea"
SORT file.ctime DESC
LIMIT 10
```