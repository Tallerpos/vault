# Dashboard de Lectura

## Inspiración Aleatoria
```dataviewjs
const ideas = dv.pages('"ideas"').where(p => p.tipo === "idea");
if (ideas.length > 0) {
    const randomIdea = ideas[Math.floor(Math.random() * ideas.length)];
    const cardStyle = `
        background: var(--background-secondary-alt);
        border-radius: 12px;
        padding: 20px;
        border-left: 5px solid var(--interactive-accent);
        margin: 10px 0;
    `;
    dv.el("div", `
        <div style="${cardStyle}">
            <div style="font-size: 0.8em; color: var(--text-muted); margin-bottom: 8px;">IDEA AL AZAR PARA REFLEXIONAR:</div>
            <div style="font-weight: 700; font-size: 1.1em; margin-bottom: 10px;">${randomIdea.file.link}</div>
            <div style="font-size: 0.9em; color: var(--text-normal); font-style: italic;">
                Fuente: ${randomIdea.fuente || "Sin fuente vinculada"}
            </div>
        </div>
    `);
}
```

---

## Biblioteca Visual (Galería)
```dataviewjs
// 1. Inyección de Estilos Premium Inline
const cardStyle = `
    background: var(--background-secondary-alt);
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--divider-color);
    display: flex;
    flex-direction: column;
    width: 190px;
    text-decoration: none;
    transition: transform 0.2s;
`;

const containerStyle = `
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    padding: 20px 0;
    width: 100%;
`;

const books = dv.pages('"Libros"')
    .where(p => p.tipo === "libro")
    .sort(p => p.rating, "desc")
    .sort(p => p.file.mtime, "desc");

if (books.length === 0) {
    dv.paragraph("No se detectaron libros en la carpeta 'Libros'.");
} else {
    let html = `<div style="${containerStyle}">`;
    for (const book of books) {
        const cover = book.portada || "https://via.placeholder.com/180x270?text=Sin+Portada";
        const ratingText = book.rating ? "Puntuación: " + book.rating + "/5" : "Sin calificar";
        html += `
            <a href="${book.file.path}" class="internal-link" style="${cardStyle}">
                <div style="width: 100%; aspect-ratio: 2/3; background: #2a2a2a; overflow: hidden;">
                    <img src="${cover}" style="width: 100%; height: 100%; object-fit: cover;">
                </div>
                <div style="padding: 12px; background: var(--background-secondary); flex-grow: 1;">
                    <div style="font-weight: 700; font-size: 0.9em; color: var(--text-normal); margin-bottom: 4px;">${book.file.name}</div>
                    <div style="font-size: 0.8em; color: var(--text-muted);">${book.autor || "Desconocido"}</div>
                    <div style="margin-top: 8px; font-size: 0.75em; color: var(--interactive-accent); font-weight: 600;">${ratingText}</div>
                </div>
            </a>
        `;
    }
    html += '</div>';
    dv.el("div", html);
}
```

---

## Alertas de Mantenimiento
```dataviewjs
const ideas = dv.pages('"ideas"').where(p => p.tipo === "idea");
const orphanIdeas = ideas.filter(i => !i.fuente || i.fuente === "" || i.fuente === "[[null]]");

const books = dv.pages('"Libros"').where(p => p.tipo === "libro");
const booksWithNoIdeas = books.filter(b => {
    const ideasForThisBook = ideas.filter(i => {
        const fuenteStr = String(i.fuente);
        return fuenteStr.includes(b.file.name);
    });
    return ideasForThisBook.length === 0;
});

if (orphanIdeas.length > 0 || booksWithNoIdeas.length > 0) {
    dv.header(3, "Atención requerida");
    if (orphanIdeas.length > 0) {
        dv.paragraph("⚠️ **Ideas sin vincular (Huérfanas):** " + orphanIdeas.map(i => i.file.link).join(", "));
    }
    if (booksWithNoIdeas.length > 0) {
        dv.paragraph("📖 **Libros sin ideas procesadas aún:** " + booksWithNoIdeas.map(b => b.file.link).join(", "));
    }
} else {
    dv.paragraph("Integridad del sistema: Óptima");
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

if (temaMap.size > 0) {
  for (const [tema, notas] of [...temaMap.entries()].sort()) {
    dv.header(3, `${tema} (${notas.length})`);
    dv.list(notas.map(n => n.file.link));
  }
}
```