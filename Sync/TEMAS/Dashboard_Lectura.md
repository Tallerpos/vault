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

dv.paragraph("No se detectaron libros en la carpeta 'BIBLIOTECA/Libros'.");

} else {

// 2. Definición Estética (Flexbox Inline - Máxima compatibilidad)

const cardStyle = "background: var(--background-secondary-alt); border-radius: 12px; overflow: hidden; border: 1px solid var(--divider-color); display: flex; flex-direction: column; width: 190px; text-decoration: none; transition: transform 0.2s;";

const containerStyle = "display: flex; flex-wrap: wrap; gap: 20px; padding: 20px 0; width: 100%;";

  

// 3. Generación del HTML

let html = `<div style="${containerStyle}">`;

for (const book of books) {

const cover = book.portada || "https://via.placeholder.com/180x270?text=Sin+Portada";

const ratingText = book.rating ? "Puntuación: " + book.rating + "/5" : "Sin calificar";

html += `

<a href="${book.file.path}" class="internal-link" style="${cardStyle}">

<div style="width: 100%; aspect-ratio: 2/3; background: #1a1a1a; overflow: hidden;">

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