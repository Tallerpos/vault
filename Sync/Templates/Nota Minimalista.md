<%*
// ============================================
// PLANTILLA: Nota Minimalista
// Filosofía: 1 carpeta, fecha en nombre, tipo fijo, cero decisiones
// ============================================

// 1. Seleccionar tipo (lista cerrada, sin expandir nunca)
const tipo = await tp.system.suggester(
  ["idea", "reunión", "aprendizaje", "persona", "proyecto", "diario"],
  ["idea", "reunion", "aprendizaje", "persona", "proyecto", "diario"],
  false,
  "Tipo de nota",
  undefined,
  "idea"
);

// 2. Título de la nota (opcional, se puede dejar vacío)
const titulo = await tp.system.prompt("Título (opcional)", "");

// 3. Fecha de hoy
const fecha = tp.date.now("YYYY-MM-DD");

// 4. Construir nombre: AAAA-MM-DD - tipo - título
const cleanTitulo = titulo.replace(/[\/\\:*?"<>|]/g, "").trim();
const filename = cleanTitulo
  ? `${fecha} - ${tipo} - ${cleanTitulo}`
  : `${fecha} - ${tipo}`;

// 5. Renombrar archivo
await tp.file.rename(filename);
-%>
---
fecha: <% tp.date.now("YYYY-MM-DD") -%>
tipo: <% tipo -%>
tags: []
relacionado: []
---

<% tp.file.cursor() %>
