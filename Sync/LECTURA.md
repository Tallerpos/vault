# 🧠 Dashboard

## Mis libros
```dataview
TABLE autor, año, rating, estado
FROM "Libros"
WHERE tipo = "libro"
SORT rating DESC
```

## Ideas por tema
```dataviewjs
const ideas = dv.pages().where(p => p.tipo === "idea");
const temaMap = new Map();

for (const idea of ideas) {
  const temas = idea.temas
    ? (Array.isArray(idea.temas) ? idea.temas : [idea.temas])
    : ["Sin tema"];
  for (const tema of temas) {
    if (!temaMap.has(tema)) temaMap.set(tema, []);
    temaMap.get(tema).push(idea);
  }
}

if (temaMap.size === 0) {
  dv.paragraph("No hay ideas con temas asignados aún.");
} else {
  for (const [tema, notas] of [...temaMap.entries()].sort()) {
    dv.header(3, tema + " (" + notas.length + ")");
    dv.list(notas.map(n => n.file.link));
  }
}
```

## Ideas recientes
```dataview
TABLE fuente, temas
FROM "ideas"
WHERE tipo = "idea"
SORT file.ctime DESC
LIMIT 10
```