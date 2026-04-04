<%*
const libros = app.vault.getMarkdownFiles()
  .filter(f => f.path.startsWith("Libros/"));
const libro = await tp.system.suggester(
  f => f.basename,
  libros,
  true,
  "¿De qué libro viene esta idea?"
);
const libroLink = libro ? `[[${libro.basename}]]` : "";
-%>
---
tipo: idea
fuente: <% libroLink %>
temas: []
---

# <% tp.file.title [[La logoterapia como paz]]%>

(Explica la idea en 3-8 líneas en tus palabras)

**Aplica cuando:**

**Falla cuando:**

Conecta con: [[]]
Contrasta con: [[]]