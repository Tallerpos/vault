<%*
// ── 1. SELECCIONAR LIBRO ──────────────────────────────
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

// ── 2. TEMAS INTELIGENTES (HERENCIA) ──────────────────
const cacheLibro = libro ? app.metadataCache.getFileCache(libro) : null;
const temasLibro = cacheLibro?.frontmatter?.temas || [];
const temasPropuestos = Array.isArray(temasLibro) ? temasLibro : [temasLibro];

// Leer temas existentes de otras ideas
const todasIdeas = app.vault.getMarkdownFiles()
  .filter(f => f.path.startsWith("ideas/"));

const temasSet = new Set(temasPropuestos); // Empezamos con los del libro
for (const idea of todasIdeas) {
  const cache = app.metadataCache.getFileCache(idea);
  const t = cache?.frontmatter?.temas;
  if (Array.isArray(t)) t.forEach(x => temasSet.add(x));
  else if (typeof t === "string" && t) temasSet.add(t);
}

const opciones = ["＋ Nuevo tema...", ...([...temasSet].sort())];
const temasElegidos = [];
let seguir = true;

while (seguir) {
  const sel = await tp.system.suggester(
    x => (temasPropuestos.includes(x) ? "📖 " : "🏷️ ") + x,
    opciones,
    false,
    `Tema #${temasElegidos.length + 1} (ESC para terminar)`
  );
  if (!sel) {
    seguir = false;
  } else if (sel === "＋ Nuevo tema...") {
    const nuevo = await tp.system.prompt("Escribe el nuevo tema:");
    if (nuevo) { temasElegidos.push(nuevo); opciones.push(nuevo); }
  } else {
    // Si elegimos un tema que ya incluye el prefijo visual
    const limpio = sel.replace(/^[📖🏷️]\s/, "");
    temasElegidos.push(limpio);
    opciones.splice(opciones.indexOf(sel), 1);
  }
}

const temasYaml = temasElegidos.length
  ? "\n" + temasElegidos.map(t => "  - " + t).join("\n")
  : " []";

// ── 3. AGREGAR LINK AL LIBRO AUTOMÁTICAMENTE ─────────
if (libro) {
  const contenido = await app.vault.read(libro);
  const ideaLink = "\n- [[" + tp.file.title + "]]";
  const actualizado = contenido.includes("## Notas brutas")
    ? contenido.replace("## Notas brutas", "## Notas brutas" + ideaLink)
    : contenido + "\n- [[" + tp.file.title + "]]";
  await app.vault.modify(libro, actualizado);
}
_%>
---
tipo: idea
fuente: "[[<% nombre %>]]"
temas:<% temasYaml %>
---

**Fuente:** [[<% nombre %>]]

# <% tp.file.title %>

(Explica la idea en tus palabras — 3 a 8 líneas)

**Por qué me importa a mí:**

**Aplica cuando:**

**Falla cuando:**

Conecta con: [[]]
Contrasta con: [[]]