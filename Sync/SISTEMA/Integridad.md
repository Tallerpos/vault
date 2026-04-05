# Mantenimiento y Auditoría de la Bóveda

Este panel detecta problemas estructurales en tu conocimiento para asegurar que todo esté conectado y normalizado.

## Ideas Huérfanas (Sin Fuente)
Notas en la carpeta /ideas que no están vinculadas a un libro maestro.
```dataview
TABLE fuente as "Fuente Actual"
FROM "ideas"
WHERE tipo = "idea" AND (fuente = null OR fuente = "" OR contains(string(fuente), "null"))
```

## Libros sin Procesar
Libros registrados que no tienen ninguna idea asociada todavía.
```dataviewjs
const ideas = dv.pages('"ideas"').where(p => p.tipo === "idea");
const books = dv.pages('"Libros"').where(p => p.tipo === "libro");

const results = books.filter(b => {
    const ideasForThisBook = ideas.filter(i => {
        const fuenteStr = String(i.fuente);
        return fuenteStr.includes(b.file.name);
    });
    return ideasForThisBook.length === 0;
});

if (results.length > 0) {
    dv.list(results.map(b => b.file.link));
} else {
    dv.paragraph("Todos los libros tienen al menos una idea asociada.");
}
```

## Análisis de Temas y Duplicados
Lista de temas únicos para detectar variaciones ortográficas (ej: "Psicología" vs "psicología").
```dataviewjs
const pages = dv.pages('"ideas" or "Libros"');
const temas = new Set();
pages.forEach(p => {
    if (p.temas) {
        if (Array.isArray(p.temas)) p.temas.forEach(t => temas.add(t));
        else temas.add(p.temas);
    }
});

dv.list([...temas].sort());
```

## Libros sin Calificar
```dataview
LIST
FROM "Libros"
WHERE tipo = "libro" AND rating = null
```
