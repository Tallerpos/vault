---
tipo: libro
autor: 
año: 
isbn: 
portada: ""
temas: []
rating: 
estado: leyendo
---

```dataviewjs
const p = dv.current();
const u_open = "\u005B\u005B";
const u_close = "\u005D\u005D";

// 1. Estadísticas automáticas
const ideasCount = dv.pages('"ideas"').filter(i => {
    return i.fuente && String(i.fuente).includes(p.file.name);
}).length;

// 2. Render de Cabecera Elite (Resiliente)
const container = this.container.createDiv({ style: "display: flex; flex-wrap: wrap; gap: 30px; padding: 25px; background: var(--background-secondary-alt); border-radius: 15px; border: 1px solid var(--divider-color); margin-bottom: 30px; min-height: 250px;" });

// Columna Imagen / Card Reemplazo
const imgCol = container.createDiv({ style: "width: 180px; min-width: 150px; flex: 0 0 180px; height: 270px; border-radius: 8px; overflow: hidden; box-shadow: 0 10px 20px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; position: relative;" });

if (p.portada && p.portada !== "") {
    imgCol.createEl("img", { 
        attr: { src: p.portada },
        style: "width: 100%; height: 100%; object-fit: cover;"
    });
} else {
    // Si no hay portada, creamos una tarjeta estética elegante
    imgCol.style.background = "linear-gradient(135deg, var(--interactive-accent) 0%, var(--background-modifier-border) 100%)";
    imgCol.createDiv({ 
        text: p.file.name, 
        style: "padding: 20px; color: white; font-weight: 700; text-align: center; font-size: 1.1em; line-height: 1.3;" 
    });
    imgCol.createDiv({ 
        text: "Libro", 
        style: "position: absolute; bottom: 10px; font-size: 0.7em; color: rgba(255,255,255,0.7); text-transform: uppercase; letter-spacing: 2px;" 
    });
}

// Columna Info
const infoCol = container.createDiv({ style: "flex: 1; min-width: 250px; display: flex; flex-direction: column; justify-content: flex-start;" });

// Titulo y Autor
const topInfo = infoCol.createDiv();
topInfo.createEl("h1", { text: p.file.name, style: "margin: 0 0 5px 0; border: none; font-size: 1.8em; line-height: 1.2; font-weight: 800;" });
topInfo.createEl("div", { text: p.autor || "Autor Desconocido", style: "font-size: 1.2em; color: var(--text-muted); font-weight: 500; margin-bottom: 20px;" });

// Badges de Estado y Conteo
const statsRow = infoCol.createDiv({ style: "display: flex; flex-wrap: wrap; gap: 12px; align-items: center; margin-top: auto;" });

// Estado
const estadoTxt = (p.estado || "Pendiente").toUpperCase();
const estadoBadge = statsRow.createDiv({ style: "padding: 6px 15px; border-radius: 6px; font-size: 0.75em; font-weight: 700; letter-spacing: 1px; background: var(--interactive-accent); color: white;" });
estadoBadge.innerText = estadoTxt;

// Contador de Ideas
const countBadge = statsRow.createDiv({ style: "padding: 6px 15px; border-radius: 6px; font-size: 0.75em; font-weight: 600; background: var(--background-primary); border: 1px solid var(--divider-color); color: var(--text-normal);" });
countBadge.innerHTML = `CONEXIONES: <b>${ideasCount}</b>`;

// Calificación (Rating)
if (p.rating) {
    const ratingRow = infoCol.createDiv({ style: "margin-top: 15px; font-size: 1.3em; color: var(--interactive-accent); letter-spacing: 3px;" });
    ratingRow.innerText = "★".repeat(p.rating) + "☆".repeat(5 - p.rating);
}
```

## Por qué lo leí

## Tesis

## Notas brutas
(Escribe aquí las ideas que surjan de la lectura)

---

## Ideas vinculadas
```dataview
LIST
FROM "ideas"
WHERE contains(file.outlinks, this.file.link) OR contains(fuente, this.file.name)
SORT file.mtime DESC
```