<%*
const tipo = await tp.system.suggester(
  ["idea", "reunión", "aprendizaje", "persona", "proyecto", "diario"],
  ["idea", "reunion", "aprendizaje", "persona", "proyecto", "diario"]
);
const fecha = tp.date.now("YYYY-MM-DD");
let carpeta = tipo === "diario" ? "Diario" : "Notas";
let titulo = "";
if (tipo !== "diario") {
  titulo = await tp.system.prompt("Título");
}
const cleanTitulo = titulo.replace(/[\/\\:*?"<>|]/g, "").trim();
const filename = tipo === "diario"
  ? fecha
  : (cleanTitulo ? `${fecha} - ${tipo} - ${cleanTitulo}` : `${fecha} - ${tipo}`);
await tp.file.move(`${carpeta}/${filename}`);
-%>
---
fecha: <% tp.date.now("YYYY-MM-DD") %>
tipo: <% tipo %>
tags: []
relacionado: []
---

<% tp.file.cursor() %>
