---
tipo: libro
autor:
año:
rating:
estado: leyendo
temas: []
---

## Por qué lo leí
(1 línea: qué problema concreto quería resolver)

## Tesis
(Al terminar: 3-5 líneas en tus palabras. Si no puedes, no terminaste de entenderlo)

## Notas brutas
(Escribe aquí lo que quieras mientras lees. Sin formato. Sin presión.)

---

## Ideas que generó este libro
```dataview
LIST
FROM "💡 Ideas"
WHERE contains(fuente, this.file.link)
SORT file.ctime ASC
```