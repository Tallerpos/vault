# 🔗 Reporte de Integridad

Este panel centraliza la reparación de tu sistema de lectura sin necesidad d scripts externos, protegiendo tu gráfico de conocimiento (Graph View) de nodos fantasmas.

## Auditoría y Reparación de Enlaces (Fuente)
Si ves una tabla abajo, significa que tienes enlaces "rotos" (texto simple). Pulsa el botón para convertirlos en enlaces reales de Obsidian adecuadamente blindados para el gráfico.

```dataviewjs
// ── 1. CONFIGURACIÓN DE CARPETAS ──────────────────────
const folderIdeas = "ideas";
const ideas = dv.pages(`"${folderIdeas}"`).where(p => p.tipo === "idea");

// ── 2. AUDITORÍA DE ENLACES ───────────────────────────
const u_open = "\u005B\u005B";
const u_close = "\u005D\u005D";

const brokenIdeas = ideas.filter(i => {
  const f = i.fuente;
  if (!f) return false;
  return !String(f).includes(u_open);
});

if (brokenIdeas.length > 0) {
  dv.header(4, "Notas con enlaces pendientes de blindaje:");
  dv.table(["Nota", "Fuente Actual"], brokenIdeas.map(i => [i.file.link, i.fuente]));
  
  const btn = this.container.createEl("button", { text: "Reparar Enlaces y Blindar Grafo" });
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
          if (fm.fuente && !String(fm.fuente).includes(u_open)) {
            fm.fuente = u_open + fm.fuente + u_close;
            count++;
          }
        });
      }
    }
    
    new Notice(`Integridad: Se han blindado y reparado ${count} enlaces.`);
    btn.innerText = "Reparación Finalizada";
    setTimeout(() => { location.reload(); }, 1500);
  };
} else {
  dv.paragraph("✅ Todos los enlaces están correctamente conectados y blindados.");
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
