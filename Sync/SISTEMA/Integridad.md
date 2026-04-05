# 🔗 Reporte de Integridad

Este panel centraliza la reparación de tu sistema sin necesidad de scripts externos, manteniendo tu bóveda limpia y profesional.

## Auditoría y Reparación de Enlaces (Fuente)
Si ves una tabla abajo, significa que tienes enlaces "rotos" (texto simple). Pulsa el botón para convertirlos en enlaces reales de Obsidian `[[ ]]`.

```dataviewjs
const ideas = dv.pages('"ideas"').where(p => p.tipo === "idea");
const brokenIdeas = ideas.filter(i => {
  const f = i.fuente;
  if (!f) return false;
  return !String(f).includes("[[");
});

if (brokenIdeas.length > 0) {
  dv.header(4, "Notas pendientes de reparación:");
  dv.table(["Nota", "Fuente Actual"], brokenIdeas.map(i => [i.file.link, i.fuente]));
  
  const btn = this.container.createEl("button", { text: "Reparar Enlaces Automáticamente" });
  btn.style.marginTop = "20px";
  btn.style.padding = "10px 20px";
  btn.style.background = "var(--interactive-accent)";
  btn.style.color = "white";
  btn.style.border = "none";
  btn.style.borderRadius = "8px";
  btn.style.cursor = "pointer";
  
  btn.onclick = async () => {
    btn.disabled = true;
    btn.innerText = "Procesando...";
    let count = 0;
    for (const idea of brokenIdeas) {
      const file = app.vault.getAbstractFileByPath(idea.file.path);
      if (file) {
        await app.fileManager.processFrontMatter(file, (fm) => {
          if (fm.fuente && !String(fm.fuente).includes("[[")) {
            fm.fuente = `[[${fm.fuente}]]`;
            count++;
          }
        });
      }
    }
    new Notice(`Integridad: Se han reparado ${count} enlaces.`);
    btn.innerText = "Reparación Finalizada";
    setTimeout(() => { location.reload(); }, 2000);
  };
} else {
  dv.paragraph("✅ Todos los enlaces están correctamente conectados.");
}
```

---

## Libros sin Notas Procesadas
```dataviewjs
const ideas = dv.pages('"ideas"').where(p => p.tipo === "idea");
const books = dv.pages('"Libros"').where(p => p.tipo === "libro");
const results = books.filter(b => !ideas.some(i => String(i.fuente).includes(b.file.name)));

if (results.length > 0) {
  dv.list(results.map(b => b.file.link));
} else {
  dv.paragraph("Correcto: Todos los libros tienen ideas asociadas.");
}
```

---

## Auditoría de Temas Únicos
```dataviewjs
const pages = dv.pages('"ideas" or "Libros"');
const temas = new Set();
pages.forEach(p => {
  if (p.temas) {
    if (Array.isArray(p.temas)) p.temas.forEach(t => temas.add(t));
    else temas.add(p.temas);
  }
});

dv.list([...temas].sort());
```
