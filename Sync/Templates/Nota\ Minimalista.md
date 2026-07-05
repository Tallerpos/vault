<%*
// 1. Obtener fecha y hora
const fecha = tp.date.now("YYYY-MM-DD");
const hora = tp.date.now("HH:mm");

// 2. Opciones de tipos con Emojis para mejor UX
const opcionesMostrar = [
    "📝 Diario", "💡 Idea", "🧠 Aprendizaje", "👥 Persona", 
    "🚀 Proyecto", "📚 Lectura/Libro", "💰 Finanzas", 
    "💻 Tecnología", "⚕️ Salud", "💼 Reunión", "🛒 Compras"
];
const opcionesValor = [
    "diario", "idea", "aprendizaje", "persona", 
    "proyecto", "lectura", "finanzas", 
    "tecnologia", "salud", "reunion", "compras"
];

let tipo = await tp.system.suggester(opcionesMostrar, opcionesValor, false, "Selecciona el tipo de nota");

if (!tipo) {
    new Notice("Creación de nota cancelada.");
    return "";
}

// 3. Determinar carpeta y título
let carpeta = tipo === "diario" ? "Diario" : "Notas";
let titulo = "";

if (tipo !== "diario") {
    titulo = await tp.system.prompt("Título (deja vacío para 'sin título')");
    if (titulo === null) {
        new Notice("Creación de nota cancelada.");
        return "";
    }
}

// Limpiar título de caracteres inválidos en filenames
const cleanTitulo = titulo ? titulo.replace(/[\\/:*?"<>|]/g, "").trim() : "";

// 4. Construir filename inteligente
let filename = "";
if (tipo === "diario") {
    filename = fecha;
} else {
    filename = cleanTitulo ? `${fecha} - ${tipo} - ${cleanTitulo}` : `${fecha} - ${tipo}`;
}

// 5. Evitar colisiones si el archivo ya existe (ej: 2 diarios el mismo día, o 2 ideas sin título)
let finalPath = `${carpeta}/${filename}`;
let suffix = 1;
while (await app.vault.adapter.exists(`${finalPath}.md`)) {
    finalPath = `${carpeta}/${filename}_${suffix}`;
    suffix++;
}

// 6. Asegurar que la carpeta existe y mover la nota
if (!(await app.vault.adapter.exists(carpeta))) {
    await app.vault.createFolder(carpeta);
}
await tp.file.move(finalPath);
-%>
---
fecha: <% fecha %>
hora: <% hora %>
tipo: <% tipo %>
tags: []
relacionado: []
---
<%* if (tipo === "diario") { %>
# Diario - <% fecha %>
<%* } else if (cleanTitulo) { %>
# <% cleanTitulo %>
<%* } else { %>
# Sin título
<%* } %>

Escribe aquí tu nota.
