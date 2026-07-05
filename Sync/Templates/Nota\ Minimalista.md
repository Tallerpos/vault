<%*
const fecha = tp.date.now("YYYY-MM-DD");
const hora = tp.date.now("HH:mm");

const opcionesMostrar = [
    "Diario", "Idea", "Aprendizaje", "Persona", 
    "Proyecto", "Lectura", "Finanzas", 
    "Tecnología", "Salud", "Reunión", "Compras"
];
const opcionesValor = [
    "diario", "idea", "aprendizaje", "persona", 
    "proyecto", "lectura", "finanzas", 
    "tecnologia", "salud", "reunion", "compras"
];

let tipo = await tp.system.suggester(opcionesMostrar, opcionesValor, false, "Clasificación inicial");

if (!tipo) {
    new Notice("Cancelado.");
    return "";
}

// 1. Enrutamiento proactivo a carpetas específicas
const folderMap = {
    "diario": "Diario",
    "proyecto": "Proyectos",
    "lectura": "Biblioteca",
    "finanzas": "Finanzas",
    "reunion": "Trabajo",
    "salud": "Salud"
};
let carpeta = folderMap[tipo] || "Notas";

// 2. Prompts inteligentes según el tipo (Proactivo)
let titulo = "";
let metadata_extra = "";

if (tipo === "reunion") {
    let persona = await tp.system.prompt("¿Con quién es la reunión?");
    titulo = persona ? `Reunión con ${persona}` : "Reunión";
    if (persona) metadata_extra += `\nparticipantes: [${persona}]`;
} else if (tipo === "lectura") {
    titulo = await tp.system.prompt("Título del libro/artículo");
    let autor = await tp.system.prompt("Autor (opcional)");
    if (autor) metadata_extra += `\nautor: ${autor}`;
} else if (tipo === "proyecto") {
    titulo = await tp.system.prompt("Nombre del proyecto");
    metadata_extra += `\nestado: activo`;
} else if (tipo === "persona") {
    titulo = await tp.system.prompt("Nombre de la persona");
} else if (tipo !== "diario") {
    titulo = await tp.system.prompt("Título de la nota (vacío = auto)");
}

if (tipo !== "diario" && titulo === null) {
    new Notice("Cancelado.");
    return "";
}

// Limpieza de caracteres prohibidos
const cleanTitulo = titulo ? titulo.replace(/[\\/:*?"<>|]/g, "").trim() : "";

// Formato de archivo
let filename = tipo === "diario" 
    ? fecha 
    : (cleanTitulo ? `${fecha} - ${tipo} - ${cleanTitulo}` : `${fecha} - ${tipo}`);

let finalPath = `${carpeta}/${filename}`;
let suffix = 1;
while (await app.vault.adapter.exists(`${finalPath}.md`)) {
    finalPath = `${carpeta}/${filename}_${suffix}`;
    suffix++;
}

// Creación automática de carpeta si no existe
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
relacionado: []<% metadata_extra %>
---
<%* if (tipo === "diario") { %>
# Diario - <% fecha %>
<%* } else if (cleanTitulo) { %>
# <% cleanTitulo %>
<%* } else { %>
# <% tipo.charAt(0).toUpperCase() + tipo.slice(1) %>
<%* } %>

Escribe aquí tu nota.
