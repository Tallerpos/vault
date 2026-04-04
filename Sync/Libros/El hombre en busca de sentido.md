---
tipo: libro
autor: <% tp.system.prompt("Autor") %>
año: <% tp.system.prompt("Año") %>
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
FROM "💡 Ideas"
WHERE contains(fuente, this.file.link)
SORT file.ctime ASC
```