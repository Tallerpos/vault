# Dashboard de Lectura

## Biblioteca Visual (Galería)
```dataviewjs
// 1. Inyección de Estilos Premium
const styles = `
.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 25px;
    padding: 24px 0;
}
.book-card {
    background: var(--background-secondary-alt);
    border-radius: 12px;
    overflow: hidden;
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s ease-in-out;
    border: 1px solid var(--divider-color);
    display: flex;
    flex-direction: column;
    text-decoration: none !important;
    backdrop-filter: blur(8px);
}
.book-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.5);
    border-color: var(--interactive-accent);
}
.book-cover-container {
    position: relative;
    width: 100%;
    aspect-ratio: 2 / 3;
    overflow: hidden;
    background: var(--background-primary);
}
.book-cover {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: scale 0.5s ease;
}
.book-card:hover .book-cover {
    scale: 1.05;
}
.book-info {
    padding: 12px;
    background: var(--background-secondary);
    flex-grow: 1;
}
.book-title {
    font-weight: 700;
    font-size: 0.9em;
    line-height: 1.4;
    margin-bottom: 4px;
    color: var(--text-normal);
}
.book-author {
    font-size: 0.8em;
    color: var(--text-muted);
}
.book-rating {
    margin-top: 8px;
    font-size: 0.75em;
    letter-spacing: 1px;
    color: var(--text-accent);
}
`;
dv.el("style", styles);

// 2. Obtener y Ordenar Libros
// Prioridad: Rating (desc) -> Última modificación (desc)
const books = dv.pages('"Libros"')
    .where(p => p.tipo === "libro")
    .sort(p => p.rating, 'desc')
    .sort(p => p.file.mtime, 'desc');

if (books.length === 0) {
    dv.paragraph("No se encontraron libros en la carpeta 'Libros'. Asegúrate de que tengan 'tipo: libro' en los metadatos.");
} else {
    // 3. Renderizar Grid de Tarjetas
    let html = '<div class="dashboard-grid">';
    for (const book of books) {
        const cover = book.portada || "https://via.placeholder.com/180x270?text=Sin+Portada";
        const rating = book.rating ? "Puntuación: " + book.rating + "/5" : "Sin calificar";
        html += `
            <a href="${book.file.path}" class="internal-link book-card">
                <div class="book-cover-container">
                    <img src="${cover}" class="book-cover">
                </div>
                <div class="book-info">
                    <div class="book-title">${book.file.name}</div>
                    <div class="book-author">${book.autor || "Autor desconocido"}</div>
                    <div class="book-rating">${rating}</div>
                </div>
            </a>
        `;
    }
    html += '</div>';
    dv.el("div", html);
}
```

---

## Ideas por Tema
```dataviewjs
const ideas = dv.pages('"ideas"').where(p => p.tipo === "idea");
const temaMap = new Map();

for (const idea of ideas) {
  const temas = idea.temas
    ? (Array.isArray(idea.temas) ? idea.temas : [idea.temas])
    : ["Sin tema"];
  for (const tema of temas) {
    if (!temaMap.has(tema)) temaMap.set(tema, []);
    temaMap.get(tema).push(idea);
  }
}

if (temaMap.size === 0) {
  dv.paragraph("No se encontraron ideas. Usa la plantilla de Idea para crear una.");
} else {
  for (const [tema, notas] of [...temaMap.entries()].sort()) {
    dv.header(3, `${tema} (${notas.length})`);
    dv.list(notas.map(n => n.file.link));
  }
}
```

---

## Ideas Recientes
```dataview
TABLE fuente as "Fuente", temas as "Temas"
FROM "ideas"
WHERE tipo = "idea"
SORT file.ctime DESC
LIMIT 10
```