<%*
const autor = await tp.system.prompt("Autor del libro");
const anio = await tp.system.prompt("Año de publicación");
-%>
---
tipo: libro
autor: <% autor %>
año: <% anio %>
rating:
estado: leyendo
temas: []
---

## Por qué lo leí

## Tesis

## Notas brutas

---

## Ideas generadas
```dataview
LIST
FROM "Ideas"
WHERE contains(file.outlinks, this.file.link)
SORT file.ctime ASC
```