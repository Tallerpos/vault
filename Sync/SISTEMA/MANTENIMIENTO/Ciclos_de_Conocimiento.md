# 🔄 Ciclos de Conocimiento (Repetición Espaciada)

Este panel te ayuda a que tu conocimiento no se oxide. Revisa estas notas para refrescar tu memoria y encontrar nuevas conexiones.

---

## 📅 Notas para Revisar Hoy
*Notas cuya fecha de revisión es menor o igual a hoy.*

```dataview
TABLE up as "Tema Padre", estado as "Estado", revisar as "Próxima Revisión"
FROM "NOTAS"
WHERE revisar <= date(today)
SORT revisar ASC
```

---

## ⚠️ Notas sin Plan de Revisión
*Notas que no tienen una fecha asignada. ¡Asígname una fecha de revisión (ej: `revisar: 2026-05-01`) para que no me pierda!*

```dataview
LIST
FROM "NOTAS"
WHERE !revisar
```

---

## 🌲 El Bosque (Estado del Conocimiento)
*Una vista rápida de cómo están madurando tus ideas.*

```dataview
TABLE count(file.name) as "Cantidad"
FROM "NOTAS"
GROUP BY estado
```

---

> [!TIP]
> **Cómo Revisar:** 
> 1. Abre la nota que te toca hoy.
> 2. Léela y añade una nueva idea o conexión.
> 3. **Cambia la fecha de `revisar`** sumándole 30 o 60 días para la próxima vez.
