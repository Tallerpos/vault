# 🧭 Tema: Psicología

Este es tu centro de control para todo lo relacionado con la mente, el comportamiento y la resiliencia.

---

## 🏗️ Estructura del Conocimiento
*Navega por las diferentes profundidades de este tema.*

### [30] Conceptos Fundamentales
*Notas atómicas en tu carpeta NOTAS que cuelgan de este tema.*

```dataview
LIST FROM "NOTAS" WHERE up = [[Psicologia]] OR contains(temas, "Psychology")
```

---

## 📖 Fuentes y Biblioteca
*Libros, artículos y videos que alimentan este tema.*

```dataview
TABLE autor as "Autor", estado as "Progreso"
FROM "BIBLIOTECA/Libros"
WHERE contains(temas, "Psychology") OR nexo = [[Psicologia]]
```

---

## 🧪 Preguntas Abiertas
*Lo que todavía no has resuelto o quieres investigar más.*

- [ ] ¿Cómo equilibrar la resiliencia con el autocuidado?
- [ ] ¿Qué papel juega la genética vs el entorno en el sentido de la vida?

---

> [!TIP]
> **Cómo usar este Tema:** 
> Cuando aprendas algo nuevo sobre psicología, crea una **Idea** y asegúrate de que su campo `up` apunte a esta nota `[[Psicologia]]`. Así, aparecerá aquí automáticamente.
