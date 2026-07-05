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

let carpeta = tipo === "diario" ? "Diario" : "Notas";
let titulo = "";

if (tipo !== "diario") {
    titulo = await tp.system.prompt("Título de la nota (vacío = auto-generar)");
    if (titulo === null) {
        new Notice("Cancelado.");
        return "";
    }
}

const cleanTitulo = titulo ? titulo.replace(/[\\/:*?"<>|]/g, "").trim() : "";

let filename = "";
if (tipo === "diario") {
    filename = fecha;
} else {
    filename = cleanTitulo ? `${fecha} - ${tipo} - ${cleanTitulo}` : `${fecha} - ${tipo}`;
}

let finalPath = `${carpeta}/${filename}`;
let suffix = 1;
while (await app.vault.adapter.exists(`${finalPath}.md`)) {
    finalPath = `${carpeta}/${filename}_${suffix}`;
    suffix++;
}

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
# <% tipo.charAt(0).toUpperCase() + tipo.slice(1) %>
<%* } %>

Escribe aquí tu nota.
