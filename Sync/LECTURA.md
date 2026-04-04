# 🧠 Dashboard

## Todos mis libros
```dataview
TABLE autor, año, rating, estado
FROM "Libros"
SORT rating DESC
```

## Ideas por tema
```dataviewjs
const ideas = dv.pages('"Ideas"');
const temaMap = new Map();

for (const idea of ideas) {
  const temas = idea.temas ? 
    (Array.isArray(idea.temas) ? idea.temas : [idea.temas]) : 
    ["Sin tema"];
  for (const tema of temas) {
    if (!temaMap.has(tema)) temaMap.set(tema, []);
    temaMap.get(tema).push(idea);
  }
}

for (const [tema, notas] of [...temaMap].sort()) {
  dv.header(3, tema + " (" + notas.length + ")");
  dv.list(notas.map(n => n.file.link));
}
```

## Ideas recientes
```dataview
LIST fuente
FROM "Ideas"
SORT file.ctime DESC
LIMIT 10
```[[DSAKDSAD]]