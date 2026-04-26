# Dashboard de Lectura

  

## Inspiración Aleatoria

```dataviewjs

const ideas = dv.pages('"NOTAS"').where(p => p.tipo === "idea");

if (ideas.length > 0) {

const randomIdea = ideas[Math.floor(Math.random() * ideas.length)];

const mainCont = this.container.createDiv();

mainCont.style.background = "var(--background-secondary-alt)";

mainCont.style.borderRadius = "12px";

mainCont.style.padding = "20px";

mainCont.style.borderLeft = "5px solid var(--interactive-accent)";

mainCont.style.margin = "10px 0";

mainCont.createEl("div", {

text: "IDEA AL AZAR PARA REFLEXIONAR",

style: "font-size: 0.7em; color: var(--text-muted); margin-bottom: 8px; font-weight: bold; letter-spacing: 1px;"

});

const titleLinkCont = mainCont.createDiv({ style: "font-weight: 700; font-size: 1.2em; margin-bottom: 5px;" });

dv.el("span", randomIdea.file.link, { container: titleLinkCont });

}

```

  

---

  

## Biblioteca Visual (Galería)

```dataviewjs

// 1. Obtener Libros Ordenados
const books = dv.pages('"BIBLIOTECA/Libros"')
.where(p => p.tipo === "libro")
.sort(p => p.rating, "desc")
.sort(p => p.file.mtime, "desc");

if (books.length === 0) {
    dv.paragraph("> [!INFO] No se detectaron libros en la carpeta 'BIBLIOTECA/Libros'.");
} else {
    // 2. Definición Estética Premium
    const containerStyle = `
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 24px;
        padding: 20px 0;
    `;
    
    const cardStyle = `
        background: var(--background-secondary);
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid var(--divider-color);
        display: flex;
        flex-direction: column;
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s ease;
        cursor: pointer;
        height: 100%;
        text-decoration: none !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    `;

    let html = `<div style="${containerStyle}">`;

    for (const book of books) {
        const cover = book.portada || "https://via.placeholder.com/180x270?text=Sin+Portada";
        const rating = book.rating ? "⭐".repeat(book.rating) : "Sin calificar";
        const status = book.estado || "Pendiente";
        const statusColor = status === "leyendo" ? "#4caf50" : (status === "terminado" ? "#2196f3" : "#ff9800");

        html += `
        <a href="${book.file.path}" class="internal-link" style="${cardStyle}">
            <div style="position: relative; width: 100%; aspect-ratio: 2/3; overflow: hidden; background: #121212;">
                <img src="${cover}" style="width: 100%; height: 100%; object-fit: cover;">
                <div style="position: absolute; top: 8px; right: 8px; background: ${statusColor}; color: white; font-size: 0.65em; padding: 2px 8px; border-radius: 10px; font-weight: bold; text-transform: uppercase;">
                    ${status}
                </div>
            </div>
            <div style="padding: 14px; flex-grow: 1; display: flex; flex-direction: column; gap: 4px;">
                <div style="font-weight: 800; font-size: 0.95em; color: var(--text-normal); line-height: 1.2; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                    ${book.file.name}
                </div>
                <div style="font-size: 0.8em; color: var(--text-muted); font-weight: 500;">
                    ${book.autor || "Autor Desconocido"}
                </div>
                <div style="margin-top: auto; padding-top: 8px; font-size: 0.75em; display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: var(--interactive-accent); font-weight: 700;">${rating}</span>
                </div>
            </div>
        </a>
        `;
    }

    html += '</div>';
    dv.el("div", html);
}

```

  

---

  

## Alertas e Integridad

```dataviewjs

const ideas = dv.pages('"NOTAS"').where(p => p.tipo === "idea");

const orphanIdeas = ideas.filter(i => !i.fuente || !String(i.fuente).includes("\u005B\u005B"));

  

if (orphanIdeas.length > 0) {

const box = this.container.createDiv({ style: "background: rgba(255, 0, 0, 0.05); padding: 10px; border-radius: 8px;" });

box.createEl("div", { text: "Atención: Tienes ideas mal enlazadas. Revia el Reporte de Integridad.", style: "font-size: 0.85em; color: var(--text-error);" });

} else {

dv.paragraph("Integridad del conocimiento: Óptima.");

}

```

  

---

  

## Ideas por Temas

```dataviewjs

const ideas = dv.pages('"NOTAS"').where(p => p.tipo === "idea");

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