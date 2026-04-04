---
título:
autor:
año:
páginas:
género:
  - 
temas:
  - 
estado: en-lectura
calificación:
fecha-inicio: 2026-04-04
fecha-fin:
isbn:
tipo: libro
---

# Libros

## ¿Por qué estoy leyendo esto?

> Escribe 1-2 oraciones: qué problema concreto resuelve este libro para ti ahora mismo.

---

## Resumen ejecutivo *(completar al terminar)*

**Tesis central en 1 oración:**

**Las 3 ideas que cambiaron mi perspectiva:**
1. 
2. 
3. 

**¿Lo recomendaría? ¿A quién?**

---

## Notas por capítulo

> Instrucción: escribe en tus propias palabras, nunca copies párrafos. Una idea = un bullet.

### Cap. 1 — 

- 

> **Reflexión personal:** ¿Esto contradice o confirma algo que ya sabía?

**Cita útil:**
> ""
> — p.

---

### Cap. 2 — 

- 

> **Reflexión personal:**

---

<!-- Duplica el bloque de capítulo según necesites -->

---

## Conceptos clave → Notas atómicas

> Cada fila debe tener su propia nota en `[[Conceptos/NombreConcepto]]`. Así el concepto es reutilizable entre libros.

| Concepto | Definición en tus palabras | Nota atómica |
|----------|---------------------------|--------------|
|  |  | [[ ]] |
|  |  | [[ ]] |

---

## Preguntas sin resolver

> Lo que el libro abrió pero no cerró. Pueden convertirse en nuevas lecturas.

- [ ] 
- [ ] 

---

## De lectura a acción

> Sin esta sección el libro no sirvió de nada.

| Acción concreta | Plazo | Hecho |
|----------------|-------|-------|
|  |  | [ ] |

---

## Citas seleccionadas

> Solo citas que usarías en una conversación real.

> ""
> — *undefined*, p.

---

## Conexiones con otros libros

**Conexiones identificadas manualmente:**
- [[Título del libro]] — *por qué se conectan (ej: mismo argumento desde otro ángulo)*

**Libros en mi vault con temas similares** *(Dataview automático)*:

```dataview
TABLE autor, calificación, temas, estado
FROM "📚 Libros"
WHERE any(temas, (t) => contains(this.temas, t))
AND file.name != this.file.name
SORT calificación DESC
```

**Todos mis libros terminados:**

```dataview
TABLE autor, calificación, fecha-fin, género
FROM "📚 Libros"
WHERE estado = "terminado"
SORT fecha-fin DESC
```

---

## Notas permanentes generadas

> Links a notas atómicas que nacieron de este libro y ahora viven en tu Zettelkasten.

- [[ ]]

---
*Actualizado: 2026-04-04*