---
cssclass: cards
---
# Dashboard de Lectura

> [!TIP]
> **Optimización Móvil (v6.1)**: Para ver la cuadrícula nativa, activa el snippet **'dashboard'** en `Ajustes > Apariencia > Snippets de CSS`.

## Inspiración Aleatoria
```dataviewjs
const ideas = dv.pages('"ideas"').where(p => p.tipo === "idea");
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
    
    const titleLinkCont = mainCont.createDiv({ style: "font-weight: 700; font-size: 1.2em; margin-bottom: 10px;" });
    dv.el("span", randomIdea.file.link, { container: titleLinkCont });
    
    const sourceEl = mainCont.createDiv({ style: "font-size: 0.9em; color: var(--text-normal); font-style: italic;" });
    sourceEl.appendText("Fuente: ");
    dv.el("span", randomIdea.fuente || "Sin fuente vinculada", { container: sourceEl });
}
```

---

## Biblioteca Visual (Galería Nativa)
```dataview
TABLE WITHOUT ID
    ("![|" + portada + "]") as "Portada",
    file.link as "Título",
    autor as "Autor",
    ("Puntuación: " + rating + "/5") as "Calificación"
FROM "Libros"
WHERE tipo = "libro"
SORT rating DESC, file.mtime DESC
```

---

## Alertas de Mantenimiento
```dataviewjs
// El panel de mantenimiento ahora es dinámico y ligero
const ideas = dv.pages('"ideas"').where(p => p.tipo === "idea");
const orphanIdeas = ideas.filter(i => {
    const f = i.fuente;
    return !f || f === "" || String(f).includes("null") || String(f) === "[]" || !String(f).includes("[[");
});

const books = dv.pages('"Libros"').where(p => p.tipo === "libro");
const booksWithNoIdeas = books.filter(b => !ideas.some(i => String(i.fuente).includes(b.file.name)));

if (orphanIdeas.length > 0 || booksWithNoIdeas.length > 0) {
    const alertBox = this.container.createDiv({
        style: "background: rgba(255, 0, 0, 0.03); border: 1px solid rgba(255, 0, 0, 0.1); border-radius: 8px; padding: 15px; margin-top: 20px;"
    });
    alertBox.createEl("h4", { text: "Acción requerida (Ver reporte de Integridad)", style: "margin: 0; color: var(--text-error); font-size: 0.9em;" });
} else {
    dv.paragraph("Estado del sistema: Conectado y estable.");
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