# Dashboard de Lectura

## Inspiración Aleatoria
```dataviewjs
const ideas = dv.pages('"ideas"').where(p => p.tipo === "idea");
if (ideas.length > 0) {
    const randomIdea = ideas[Math.floor(Math.random() * ideas.length)];
    const container = this.container.createDiv();
    container.style.background = "var(--background-secondary-alt)";
    container.style.borderRadius = "12px";
    container.style.padding = "20px";
    container.style.borderLeft = "5px solid var(--interactive-accent)";
    container.style.margin = "10px 0";

    container.createEl("div", { 
        text: "IDEA AL AZAR PARA REFLEXIONAR", 
        style: "font-size: 0.7em; color: var(--text-muted); margin-bottom: 8px; font-weight: bold; letter-spacing: 1px;" 
    });
    
    const titleLink = container.createEl("div", { 
        style: "font-weight: 700; font-size: 1.2em; margin-bottom: 10px;" 
    });
    dv.append(titleLink, randomIdea.file.link);
    
    const sourceEl = container.createEl("div", { 
        style: "font-size: 0.9em; color: var(--text-normal); font-style: italic;" 
    });
    sourceEl.appendText("Fuente: ");
    dv.append(sourceEl, randomIdea.fuente || "Sin fuente vinculada");
}
```

---

## Biblioteca Visual (Galería)
```dataviewjs
// 1. Obtener Libros Ordenados
const books = dv.pages('"Libros"')
    .where(p => p.tipo === "libro")
    .sort(p => p.rating, "desc")
    .sort(p => p.file.mtime, "desc");

if (books.length === 0) {
    dv.paragraph("No se detectaron libros en la carpeta 'Libros'.");
} else {
    // 2. Contenedor de Galería
    const gallery = this.container.createDiv();
    gallery.style.display = "flex";
    gallery.style.flexWrap = "wrap";
    gallery.style.gap = "25px";
    gallery.style.padding = "20px 0";

    for (const book of books) {
        const cover = book.portada || "https://via.placeholder.com/180x270?text=Sin+Portada";
        const rating = book.rating ? "Puntuación: " + book.rating + "/5" : "Sin calificar";
        
        const card = gallery.createEl("a", { 
            cls: "internal-link",
            href: book.file.path
        });
        card.style.background = "var(--background-secondary-alt)";
        card.style.borderRadius = "14px";
        card.style.overflow = "hidden";
        card.style.border = "1px solid var(--divider-color)";
        card.style.display = "flex";
        card.style.flexDirection = "column";
        card.style.width = "190px";
        card.style.textDecoration = "none";
        card.style.color = "inherit";

        // Imagen
        const imgCont = card.createDiv({ style: "width: 100%; aspect-ratio: 2/3; background: #1a1a1a; overflow: hidden;" });
        imgCont.createEl("img", { attr: { src: cover }, style: "width: 100%; height: 100%; object-fit: cover;" });

        // Info
        const info = card.createDiv({ style: "padding: 15px; background: var(--background-secondary); flex-grow: 1;" });
        info.createDiv({ text: book.file.name, style: "font-weight: 700; font-size: 0.95em; color: var(--text-normal); margin-bottom: 5px; line-height: 1.3;" });
        info.createDiv({ text: book.autor || "Desconocido", style: "font-size: 0.8em; color: var(--text-muted);" });
        info.createDiv({ text: rating, style: "margin-top: 10px; font-size: 0.75em; color: var(--interactive-accent); font-weight: 600;" });
    }
}
```

---

## Alertas de Mantenimiento
```dataviewjs
const ideas = dv.pages('"ideas"').where(p => p.tipo === "idea");
const orphanIdeas = ideas.filter(i => {
    const f = i.fuente;
    return !f || f === "" || String(f).includes("null") || String(f) === "[]";
});

const books = dv.pages('"Libros"').where(p => p.tipo === "libro");
const booksWithNoIdeas = books.filter(b => {
    const ideasForThisBook = ideas.filter(i => String(i.fuente).includes(b.file.name));
    return ideasForThisBook.length === 0;
});

if (orphanIdeas.length > 0 || booksWithNoIdeas.length > 0) {
    const alertBox = this.container.createDiv({
        style: "background: rgba(255, 0, 0, 0.05); border: 1px solid rgba(255, 0, 0, 0.2); border-radius: 8px; padding: 15px; margin-top: 20px;"
    });
    alertBox.createEl("h3", { text: "Atención Requerida", style: "margin-top: 0; color: var(--text-error); font-size: 1em;" });
    
    if (orphanIdeas.length > 0) {
        const p = alertBox.createEl("p", { style: "font-size: 0.9em; margin-bottom: 8px;" });
        p.createEl("strong", { text: "Ideas sin vincular: " });
        orphanIdeas.forEach((id, index) => {
            dv.append(p, id.file.link);
            if (index < orphanIdeas.length -1) p.appendText(", ");
        });
    }
    
    if (booksWithNoIdeas.length > 0) {
        const p = alertBox.createEl("p", { style: "font-size: 0.9em; margin: 0;" });
        p.createEl("strong", { text: "Libros sin ideas aún: " });
        booksWithNoIdeas.forEach((bk, index) => {
            dv.append(p, bk.file.link);
            if (index < booksWithNoIdeas.length -1) p.appendText(", ");
        });
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