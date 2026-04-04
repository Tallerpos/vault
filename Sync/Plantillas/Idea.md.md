<%*
const libros = app.vault.getMarkdownFiles()
  .filter(f => f.path.startsWith("Libros/"));
const libro = await tp.system.suggester(
  f => f.basename,
  libros,
  true,
  "¿De qué libro viene esta idea?"
);
const nombre = libro ? libro.basename : "";
const link = nombre ? "[[" + nombre + "]]" : "";
-%>
---
tipo: idea
fuente: <% link %>
temas: []
---

**Fuente:** <% link %>

# <% tp.file.title %>

(Explica la idea en tus palabras, 3-8 líneas)

**Aplica cuando:**

**Falla cuando:**

Conecta con: [[]]
Contrasta con: [[]]