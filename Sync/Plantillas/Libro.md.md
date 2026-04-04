<%*
const autor = await tp.system.prompt("Autor");
const anio = await tp.system.prompt("Año");
_%>
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
FROM "ideas"
WHERE contains(file.outlinks, this.file.link)
SORT file.ctime ASC
```