---
tipo: libro
autor: DSADAS
año: DASDSD
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