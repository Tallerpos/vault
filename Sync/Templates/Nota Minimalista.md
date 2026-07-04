<%*
// ============================================
// PLANTILLA: Nota Minimalista v3
// Completamente automática, cero fricción
// ============================================

// 1. Seleccionar tipo
const tipo = await tp.system.suggester(
  ["idea", "reunión", "aprendizaje", "persona", "proyecto", "diario"],
  ["idea", "reunion", "aprendizaje", "persona", "proyecto", "diario"]
);

// 2. Determinar carpeta y nombre automáticamente
const fecha = tp.date.now("YYYY-MM-DD");
let carpeta, titulo, filename;

if (tipo === "diario") {
  // Diario: sin título, solo fecha
  carpeta = "Diario";
  filename = fecha;
  titulo = "";
} else {
  // Otros: pedir título
  carpeta = "Notas";
  titulo = await tp.system.prompt("Título");
  const cleanTitulo = titulo.replace(/[\/\\:*?"<>|]/g, "").trim();
  filename = cleanTitulo
    ? `${fecha} - ${tipo} - ${cleanTitulo}`
    : `${fecha} - ${tipo}`;
}

// 3. Mover archivo
await tp.file.move(`${carpeta}/${filename}`);
-%>
---
fecha: <% tp.date.now("YYYY-MM-DD") %>
tipo: <% tipo %>
tags: []
relacionado: []
---

<% tp.file.cursor() %>
