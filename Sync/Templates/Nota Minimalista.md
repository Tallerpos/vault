---
ai_tags: [automatización, sistema, clasificación]
ai_category: tecnologia
ai_summary: Nota de configuración del sistema de clasificación automática para vault de conocimiento personal, que define
  el prompt de clasificación y la estructura de respuesta JSON.
ai_importance: 3
ai_key_topics: [plantilla, organización, metadatos]
ai_classified_at: '2026-07-05T00:21:26.727253+00:00'
---
<%*
const tipo = await tp.system.suggester(
  ["diario", "aprendizaje", "idea", "proyecto", "reunión", "persona", "lectura", "finanzas", "tecnología", "salud"],
  ["diario", "aprendizaje", "idea", "proyecto", "reunion", "persona", "lectura", "finanzas", "tecnologia", "salud"]
);
const fecha = tp.date.now("YYYY-MM-DD");
let carpeta = tipo === "diario" ? "Diario" : "Notas";
let titulo = "";
if (tipo !== "diario") {
  titulo = await tp.system.prompt("Sítulo");
}
const cleanTitulo = titulo.replace(/[\\/:*?"<>|]/g, "").trim();
const filename = tipo === "diario"
  ? fecha
  : (cleanTitulo ? `${fecha} - ${tipo} - ${cleanTitulo}` : `${fecha} - ${tipo}`);
await tp.file.move(`${carpeta}/${filename}`);
%>
---
fecha: <% fecha %>
tipo: <% tipo %>
tags: []
relacionado: []
---
