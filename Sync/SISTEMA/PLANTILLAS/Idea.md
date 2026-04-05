<%*
// ── 1. SELECCIONAR LIBRO ──────────────────────────────────────────────────────
const libros = app.vault.getMarkdownFiles()
    .filter(f => f.path.startsWith("BIBLIOTECA/Libros/"))
    .sort((a, b) => b.stat.mtime - a.stat.mtime); // más recientes primero

if (libros.length === 0) {
    new Notice("⚠ No hay libros en BIBLIOTECA/Libros/. Crea uno primero.");
    return;
}

const libro = await tp.system.suggester(
    f => {
        const cache = app.metadataCache.getFileCache(f);
        const autor = cache?.frontmatter?.autor ? ` · ${cache.frontmatter.autor}` : "";
        const estado = cache?.frontmatter?.estado ? ` [${cache.frontmatter.estado}]` : "";
        return `${f.basename}${autor}${estado}`;
    },
    libros,
    true,
    "¿De qué libro viene esta idea? (ESC = sin libro)"
);

const nombreLibro = libro ? libro.basename : "";
const linkLibro   = nombreLibro ? `[[${nombreLibro}]]` : "";

// ── 2. PÁGINA / CAPÍTULO OPCIONAL ─────────────────────────────────────────────
let ubicacion = "";
if (libro) {
    const pag = await tp.system.prompt("Página o capítulo (opcional, Enter para omitir)");
    if (pag && pag.trim() !== "") {
        ubicacion = pag.trim();
    }
}

// ── 3. TEMAS INTELIGENTES (HERENCIA + POOL GLOBAL) ───────────────────────────
const cacheLibro    = libro ? app.metadataCache.getFileCache(libro) : null;
const temasLibroRaw = cacheLibro?.frontmatter?.temas || [];
const temasLibro    = Array.isArray(temasLibroRaw)
    ? temasLibroRaw.map(t => String(t))
    : [String(temasLibroRaw)].filter(Boolean);

// Recopilar todos los temas existentes en ideas
const todasIdeas = app.vault.getMarkdownFiles()
    .filter(f => f.path.startsWith("NOTAS/"));

const temasSet = new Set(temasLibro);
for (const idea of todasIdeas) {
    const cache = app.metadataCache.getFileCache(idea);
    const t = cache?.frontmatter?.temas;
    if (Array.isArray(t))          t.forEach(x => temasSet.add(String(x)));
    else if (typeof t === "string" && t) temasSet.add(t);
}

// Loop de selección — marca los ya elegidos y los del libro
const temasElegidos = new Set();
let opcionesDisponibles = ["＋ Nuevo tema...", ...([...temasSet].sort())];
let seguir = true;

while (seguir) {
    const label = (x) => {
        if (x === "＋ Nuevo tema...") return x;
        const yaElegido  = temasElegidos.has(x) ? "✓ " : "   ";
        const esDelLibro = temasLibro.includes(x) ? "[Libro] " : "[General] ";
        return `${yaElegido}${esDelLibro}${x}`;
    };

    const sel = await tp.system.suggester(
        label,
        opcionesDisponibles,
        false,
        `Temas seleccionados: ${temasElegidos.size} — (ESC para terminar)`
    );

    if (!sel) {
        seguir = false;
    } else if (sel === "＋ Nuevo tema...") {
        const nuevo = await tp.system.prompt("Escribe el nuevo tema:");
        if (nuevo && nuevo.trim()) {
            const n = nuevo.trim();
            temasElegidos.add(n);
            opcionesDisponibles.push(n);
        }
    } else {
        // Toggle: si ya está elegido, deseleccionarlo
        if (temasElegidos.has(sel)) {
            temasElegidos.delete(sel);
        } else {
            temasElegidos.add(sel);
        }
    }
}

const temasFinal = [...temasElegidos];
const temasYaml  = temasFinal.length
    ? "\n" + temasFinal.map(t => `  - "${t}"`).join("\n")
    : " []";

// ── 4. FECHA HOY ──────────────────────────────────────────────────────────────
const fechaHoy = tp.date.now("YYYY-MM-DD");

// ── 5. MOVER A CARPETA CORRECTA ───────────────────────────────────────────────
// Garantiza que la idea siempre esté en ideas/ para que la herencia funcione
const rutaActual = tp.file.path(true);
if (!rutaActual.startsWith("NOTAS/")) {
    const safeTitle = tp.file.title.replace(/[\\/#^[\]|:]/g, "").trim();
    await tp.file.move(`NOTAS/${safeTitle}`);
}

// ── 6. INSERTAR LINK EN EL LIBRO (patch robusto) ─────────────────────────────
if (libro) {
    const contenido  = await app.vault.read(libro);
    const ideaLink   = `\n- [[${tp.file.title}]]`;
    const headingRx  = /(##\s*Notas brutas)/i;

    let actualizado;
    if (headingRx.test(contenido)) {
        // Evitar duplicados: solo insertar si el link no existe ya
        if (!contenido.includes(`[[${tp.file.title}]]`)) {
            actualizado = contenido.replace(headingRx, `$1${ideaLink}`);
        } else {
            actualizado = contenido; // ya está vinculada, no tocar
        }
    } else {
        actualizado = contenido + `\n\n## Notas brutas${ideaLink}`;
    }

    await app.vault.modify(libro, actualizado);
}
_%>
---
tipo: idea
fuente: "<% linkLibro %>"
<% ubicacion ? `ubicacion: "${ubicacion}"` : "ubicacion: " %>
fecha: <% fechaHoy %>
temas:<% temasYaml %>
---

**Fuente:** <% linkLibro %><% ubicacion ? ` · p. ${ubicacion}` : "" %>

# <% tp.file.title %>

*(Explica la idea en tus propias palabras — 3 a 8 líneas)*

**Por qué me importa:**

**Aplica cuando:**

**Falla cuando:**

**Conecta con:** 
**Contrasta con:**