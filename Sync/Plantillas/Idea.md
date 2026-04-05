<%*
// ── 1. SELECCIONAR LIBRO ──────────────────────────────
const libros = app.vault.getMarkdownFiles()
  .filter(f => f.path.startsWith("Libros/"));

if (libros.length === 0) {
  new Notice("Crea un libro primero para poder asociar esta idea.");
  return;
}

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
const temasLibroRaw = cacheLibro?.frontmatter?.temas || [];
const temasLibro = Array.isArray(temasLibroRaw) ? temasLibroRaw : [temasLibroRaw];

// Leer temas existentes de otras ideas
const todasIdeas = app.vault.getMarkdownFiles()
  .filter(f => f.path.startsWith("ideas/"));

const temasSet = new Set(temasLibro);
for (const idea of todasIdeas) {
  const cache = app.metadataCache.getFileCache(idea);
  const t = cache?.frontmatter?.temas;
  if (Array.isArray(t)) t.forEach(x => temasSet.add(x));
  else if (typeof t === "string" && t) temasSet.add(t);
}

const opciones = ["＋ Nuevo tema...", ...([...temasSet].sort())];
const temasElegidos = new Set();
let seguir = true;

while (seguir) {
  const sel = await tp.system.suggester(
    x => (temasLibro.includes(x) ? "[Libro] " : "[General] ") + (x === "＋ Nuevo tema..." ? x : x),
    opciones,
    false,
    `Tema #${temasElegidos.size + 1} (ESC para terminar)`
  );
  
  if (!sel) {
    seguir = false;
  } else if (sel === "＋ Nuevo tema...") {
    const nuevo = await tp.system.prompt("Escribe el nuevo tema:");
    if (nuevo) { temasElegidos.add(nuevo); opciones.push(nuevo); }
  } else {
    const limpio = sel.replace(/^\[.*?\]\s/, "");
    temasElegidos.add(limpio);
  }
}

const temasFinal = [...temasElegidos];
const temasYaml = temasFinal.length
  ? "\n" + temasFinal.map(t => "  - " + t).join("\n")
  : " []";

// ── 3. AGREGAR LINK AL LIBRO AUTOMÁTICAMENTE ─────────
if (libro) {
  const contenido = await app.vault.read(libro);
  const ideaLink = "\n- [[" + tp.file.title + "]]";
  const actualizado = contenido.includes("## Notas brutas")
    ? contenido.replace("## Notas brutas", "## Notas brutas" + ideaLink)
    : (contenido + "\n## Notas brutas" + ideaLink);
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