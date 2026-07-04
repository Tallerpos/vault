<%*
// ============================================
// PLANTILLA: Nota Minimalista v2
// Incluye selección de carpeta automática
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

// 2. Seleccionar carpeta destino
const carpeta = await tp.system.suggester(
  ["Notas", "Diario"],
  ["Notas", "Diario"],
  false,
  "¿Dónde guardar?",
  undefined,
  "Notas"
);

// 3. Título de la nota (opcional, se puede dejar vacío)
const titulo = await tp.system.prompt("Título (opcional)", "");

// 4. Fecha de hoy
const fecha = tp.date.now("YYYY-MM-DD");

// 5. Construir nombre: AAAA-MM-DD - tipo - título
const cleanTitulo = titulo.replace(/[\/\\:*?"<>|]/g, "").trim();
const filename = cleanTitulo
  ? `${fecha} - ${tipo} - ${cleanTitulo}`
  : `${fecha} - ${tipo}`;

// 6. Mover archivo a la carpeta seleccionada
await tp.file.move(`${carpeta}/${filename}`);
-%>
---
fecha: <% tp.date.now("YYYY-MM-DD") -%>
tipo: <% tipo -%>
tags: []
relacionado: []
---

<% tp.file.cursor() %>
