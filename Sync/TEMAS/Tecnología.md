# 🧭 Tema: Tecnología

Este es tu centro de control para todo lo relacionado con **Tecnología**.

---

## 🏗️ Estructura del Conocimiento

### Conceptos y Notas

```dataview
LIST FROM "NOTAS" WHERE contains(temas, "Tecnología") OR up = [[Tecnología]]
```

---

## 📖 Fuentes y Biblioteca

```dataview
TABLE autor as "Autor", estado as "Progreso"
FROM "BIBLIOTECA/Libros"
WHERE contains(temas, "Tecnología") OR nexo = [[Tecnología]]
```
