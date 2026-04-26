---
tipo: tema
icon: 🧭
---

# 🧭 Tema: {{name}}

Este es tu centro de control para todo lo relacionado con **{{name}}**.

---

## 🏗️ Estructura del Conocimiento

### Conceptos y Notas
```dataview
LIST FROM "NOTAS" WHERE contains(temas, "{{name}}") OR up = [[{{name}}]]
```

---

## 📖 Fuentes y Biblioteca

```dataview
TABLE autor as "Autor", estado as "Progreso", rating as "⭐"
FROM "BIBLIOTECA/Libros"
WHERE contains(temas, "{{name}}") OR nexo = [[{{name}}]]
SORT rating DESC
```

---

## 🔗 Conexiones
- [[MAPA|🗺️ Volver al Mapa]]
- [[index|🧠 Home]]
