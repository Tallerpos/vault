# LECTURA
> [!SUCCESS]
> **Sincronización Corregida**: Veo que tus archivos ya están sincronizados. He "escondido" el diseño técnico para que el Dashboard se vea limpio y profesional.

```dataviewjs
// ── INYECCIÓN SILENCIOSA DE ESTILOS (v6.4) ──
const styles = `
.cards .dataview.table-view-table {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 25px !important;
    justify-content: flex-start !important;
    width: 100% !important;
}
.cards .dataview.table-view-table thead { display: none !important; }
.cards .dataview.table-view-table tbody { display: contents !important; }
.cards .dataview.table-view-table tr {
    display: flex !important;
    flex-direction: column !important;
    width: 190px !important;
    background: var(--background-secondary-alt) !important;
    border: 1px solid var(--divider-color) !important;
    border-radius: 14px !important;
    overflow: hidden !important;
    transition: transform 0.2s !important;
    flex-grow: 1 !important;
    max-width: 210px !important;
}
.cards .dataview.table-view-table tr:hover {
    transform: translateY(-8px) !important;
    border-color: var(--interactive-accent) !important;
}
.cards .dataview.table-view-table td {
    padding: 12px !important;
    display: block !important;
    border: none !important;
}
.cards .dataview.table-view-table td:first-child {
    padding: 0 !important;
    aspect-ratio: 2 / 3 !important;
    order: -1 !important;
}
.cards .dataview.table-view-table td:first-child img {
    width: 100% !important;
    height: 100% !important;
    object-fit: cover !important;
}
.cards .dataview.table-view-table td:nth-child(2) {
    font-weight: 700 !important;
    font-size: 0.95em !important;
    color: var(--text-normal) !important;
}
.cards .dataview.table-view-table td:nth-child(n+3) {
    font-size: 0.8em !important;
    padding-top: 0 !important;
}
`;
this.container.createEl("style", { text: styles });
```

---
cssclass: cards
---

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
        style: "font-size: 0.7em; color: var(--text-muted); margin-bottom: 8px; font-weight: bold;" 
    });
    
    const titleLinkCont = mainCont.createDiv({ style: "font-weight: 700; font-size: 1.2em; margin-bottom: 5px;" });
    dv.el("span", randomIdea.file.link, { container: titleLinkCont });
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

## Alertas e Integridad
```dataviewjs
const ideas = dv.pages('"ideas"').where(p => p.tipo === "idea");
const orphanIdeas = ideas.filter(i => !i.fuente || !String(i.fuente).includes("[["));

if (orphanIdeas.length > 0) {
    const box = this.container.createDiv({ style: "background: rgba(255, 0, 0, 0.05); padding: 10px; border-radius: 8px;" });
    box.createEl("div", { text: "⚠️ Tienes ideas huérfanas o mal enlazadas. Revisa SISTEMA/Integridad.md.", style: "font-size: 0.85em; color: var(--text-error);" });
} else {
    dv.paragraph("Red de conocimiento: Estable y conectada.");
}
```