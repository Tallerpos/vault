# 🧠 Centro de Conocimiento

## 📚 Biblioteca Visual (Galería)
```dataviewjs
// 1. Inject Styles
const styles = `
.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 20px;
    padding: 20px 0;
}
.book-card {
    background: var(--background-secondary) !important;
    border-radius: 12px;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
    border: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    text-decoration: none !important;
}
.book-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.4);
    border-color: var(--interactive-accent);
}
.book-cover {
    width: 100%;
    height: 250px;
    object-fit: cover;
    background: #2a2a2a;
}
.book-info { padding: 12px; }
.book-title {
    font-weight: 600;
    font-size: 0.95em;
    color: var(--text-normal);
}
.book-author { font-size: 0.8em; color: var(--text-muted); }
`;
dv.el("style", styles);

// 2. Fetch Books
const books = dv.pages('"Libros"').where(p => p.tipo === "libro");

if (books.length === 0) {
    dv.paragraph("⚠️ No se encontraron libros en la carpeta 'Libros'. Asegúrate de que tengan `tipo: libro` en el YAML.");
} else {
    // 3. Render Card Grid
    let html = '<div class="dashboard-grid">';
    for (const book of books) {
        const cover = book.portada || "https://via.placeholder.com/180x250?text=Sin+Portada";
        html += `
            <a href="${book.file.path}" class="internal-link book-card">
                <img src="${cover}" class="book-cover">
                <div class="book-info">
                    <div class="book-title">${book.file.name}</div>
                    <div class="book-author">${book.autor || "Desconocido"}</div>
                </div>
            </a>
        `;
    }
    html += '</div>';
    dv.el("div", html);
}
```

---

## 🏷️ Ideas por Tema
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
  dv.paragraph("ℹ️ No hay ideas aún. Usa la plantilla de Idea para crear una.");
} else {
  for (const [tema, notas] of [...temaMap.entries()].sort()) {
    dv.header(3, `🏷️ ${tema} (${notas.length})`);
    dv.list(notas.map(n => n.file.link));
  }
}
```

---

## ⏱️ Ideas Recientes
```dataview
TABLE fuente as "Origen", temas as "Temas"
FROM "ideas"
WHERE tipo = "idea"
SORT file.ctime DESC
LIMIT 10
```