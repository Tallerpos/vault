<style>
.db-container { display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 30px; }
.db-stat-card { 
    background: var(--background-secondary-alt); 
    border: 1px solid var(--divider-color); 
    border-radius: 12px; 
    padding: 15px 20px; 
    flex: 1; 
    min-width: 150px; 
    text-align: center;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}
.db-stat-val { font-size: 1.8em; font-weight: 800; color: var(--interactive-accent); line-height: 1.2; }
.db-stat-label { font-size: 0.7em; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; margin-top: 5px; }

.db-progress-container { margin: 15px 0; background: var(--background-secondary-alt); border-radius: 12px; padding: 15px; border-left: 4px solid var(--interactive-accent); }
.db-progress-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.db-progress-bar-bg { background: rgba(128,128,128,0.1); height: 8px; border-radius: 4px; overflow: hidden; }
.db-progress-bar-fill { height: 100%; background: var(--interactive-accent); transition: width 0.5s ease; }

.db-gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 20px; padding: 10px 0; }
.db-card { 
    background: var(--background-secondary); 
    border-radius: 10px; 
    overflow: hidden; 
    border: 1px solid var(--divider-color); 
    transition: all 0.2s ease;
    text-decoration: none !important;
}
.db-card:hover { transform: translateY(-5px); box-shadow: 0 8px 15px rgba(0,0,0,0.2); border-color: var(--interactive-accent); }
.db-card-img { width: 100%; aspect-ratio: 2/3; object-fit: cover; background: #1a1a1a; display: block; }
.db-card-info { padding: 10px; }
.db-card-title { font-weight: 700; font-size: 0.85em; color: var(--text-normal); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.db-card-meta { font-size: 0.75em; color: var(--text-muted); }
.db-card-rating { margin-top: 5px; color: #ffd700; font-size: 0.8em; }

.db-quote { 
    background: var(--background-primary-alt); 
    border-radius: 16px; 
    padding: 30px; 
    text-align: center; 
    font-style: italic; 
    position: relative;
    border: 1px solid var(--divider-color);
    margin: 20px 0;
}
.db-quote::before { content: '"'; font-size: 4em; color: var(--interactive-accent); opacity: 0.2; position: absolute; top: 10px; left: 20px; }
</style>

# 📚 Dashboard de Lectura

## 📊 Estadísticas Globales
```dataviewjs
const books = dv.pages('"Libros"').where(p => p.tipo === "libro");
const ideas = dv.pages('"ideas"').where(p => p.tipo === "idea");

const finished = books.where(p => p.estado === "terminado").length;
const reading = books.where(p => p.estado === "leyendo").length;
const readPages = books.values.reduce((sum, p) => sum + (p.pagina_actual || 0), 0);

const html = `
<div class="db-container">
    <div class="db-stat-card"><div class="db-stat-val">${books.length}</div><div class="db-stat-label">Libros Totales</div></div>
    <div class="db-stat-card"><div class="db-stat-val">${finished}</div><div class="db-stat-label">Terminados</div></div>
    <div class="db-stat-card"><div class="db-stat-val">${ideas.length}</div><div class="db-stat-label">Ideas Capturadas</div></div>
    <div class="db-stat-card"><div class="db-stat-val">${readPages}</div><div class="db-stat-label">Páginas Leídas</div></div>
</div>
`;
dv.el("div", html);
```

---

## 📖 Leyendo Ahora
```dataviewjs
const active = dv.pages('"Libros"').where(p => p.estado === "leyendo");

if (active.length > 0) {
    for (const book of active) {
        const total = book.paginas || 1;
        const current = book.pagina_actual || 0;
        const pct = Math.min(100, Math.round((current / total) * 100));
        
        const html = `
        <div class="db-progress-container">
            <div class="db-progress-header">
                <div>
                    <span style="font-weight: 700; font-size: 1.1em;">${book.file.link}</span>
                    <br><span style="font-size: 0.8em; color: var(--text-muted);">${book.autor || "---"}</span>
                </div>
                <div style="text-align: right;">
                    <span style="font-weight: 700; color: var(--interactive-accent);">${pct}%</span>
                    <br><span style="font-size: 0.7em; color: var(--text-muted);">${current} / ${total} pág.</span>
                </div>
            </div>
            <div class="db-progress-bar-bg">
                <div class="db-progress-bar-fill" style="width: ${pct}%"></div>
            </div>
        </div>
        `;
        dv.el("div", html);
    }
} else {
    dv.paragraph("No tienes lecturas activas. ¿Qué tal empezar una nueva?");
}
```

---

## ✨ Inspiración Aleatoria
```dataviewjs
const ideas = dv.pages('"ideas"').where(p => p.tipo === "idea");
if (ideas.length > 0) {
    const randomIdea = ideas[Math.floor(Math.random() * ideas.length)];
    const quoteHtml = `
    <div class="db-quote">
        <div style="font-size: 1.2em; margin-bottom: 15px; color: var(--text-normal);">${randomIdea.file.name}</div>
        <div style="font-size: 0.85em; color: var(--interactive-accent); font-weight: 600;">${randomIdea.fuente || "---"}</div>
    </div>
    `;
    dv.el("div", quoteHtml);
}
```

---

## 🏛️ Biblioteca Completa
```dataviewjs
const books = dv.pages('"Libros"').where(p => p.tipo === "libro").sort(p => p.file.mtime, "desc");

const states = {
    "leyendo": "📖 Leyendo",
    "por leer": "⏳ Pendientes",
    "terminado": "✅ Terminados"
};

for (const [state, label] of Object.entries(states)) {
    const subset = books.where(p => p.estado === state);
    if (subset.length === 0) continue;
    
    dv.header(3, label + " (" + subset.length + ")");
    let html = `<div class="db-gallery">`;
    
    for (const b of subset) {
        const cover = b.portada || "https://via.placeholder.com/180x270?text=Sin+Portada";
        const stars = b.rating ? "★".repeat(parseInt(b.rating)) + "☆".repeat(5-parseInt(b.rating)) : "";
        
        html += `
        <a href="${b.file.path}" class="db-card internal-link">
            <img src="${cover}" class="db-card-img">
            <div class="db-card-info">
                <div class="db-card-title">${b.file.name}</div>
                <div class="db-card-meta">${b.autor || "---"}</div>
                ${stars ? `<div class="db-card-rating">${stars}</div>` : ""}
            </div>
        </a>
        `;
    }
    html += `</div>`;
    dv.el("div", html);
}
```

---

## 🏷️ Temas y Categorías
```dataviewjs
const ideas = dv.pages('"ideas"').where(p => p.tipo === "idea");
const labels = {};

ideas.forEach(i => {
    const tags = Array.isArray(i.temas) ? i.temas : (i.temas ? [i.temas] : ["Sin tema"]);
    tags.forEach(t => {
        if (!labels[t]) labels[t] = 0;
        labels[t]++;
    });
});

const sortedLabels = Object.entries(labels).sort((a,b) => b[1] - a[1]);
let tagCloud = `<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px;">`;
sortedLabels.forEach(([tag, count]) => {
    tagCloud += `<span style="background: var(--background-secondary-alt); border: 1px solid var(--divider-color); padding: 4px 12px; border-radius: 20px; font-size: 0.8em; color: var(--text-muted);">${tag} <b style="color: var(--interactive-accent)">${count}</b></span>`;
});
tagCloud += `</div>`;
dv.el("div", tagCloud);
```

---

## 🔗 Auditoría Directa
```dataviewjs
const ideas = dv.pages('"ideas"').where(p => p.tipo === "idea");
const orphanIdeas = ideas.filter(i => !i.fuente || !String(i.fuente).includes("[["));

if (orphanIdeas.length > 0) {
    dv.el("div", `⚠️ Tienes **${orphanIdeas.length}** ideas sin fuente asignada.`, { style: "color: var(--text-error); background: rgba(255,0,0,0.05); padding: 10px; border-radius: 8px;" });
} else {
    dv.el("div", "✨ Todas las ideas están correctamente enlazadas.", { style: "color: var(--text-success); font-size: 0.9em; opacity: 0.8;" });
}
```