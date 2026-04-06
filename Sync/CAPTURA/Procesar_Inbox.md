# 🏗️ Procesador de Captura (Pipeline)

Este archivo es tu mesa de trabajo semanal. Úsalo para limpiar el caos de `CAPTURA` y moverlo a la red de tu cerebro.

---

## 📥 Bandeja de Entrada (Captura)
*Estas son notas que tomaste rápido pero aún no tienen una estructura.*

```dataview
LIST
FROM "CAPTURA"
WHERE file.name != "Procesar_Inbox"
AND !contains(file.path, "Diario")
```

---

## 🛠️ Cómo Procesar una Nota:
1.  **Abre la nota suelta** desde la lista de arriba.
2.  **Limpia el texto**: Escríbela en tus propias palabras.
3.  **Aplica la Plantilla `Idea`**: (Abre comando Obsidian -> `Templater: Insert template` -> `Idea`).
4.  **Enlázala**: Elige el **Tema Padre** (un archivo en `TEMAS/`).
5.  **Próxima Revisión**: Asegúrate de que tenga una fecha en `revisar`.

---

## ✅ Lista de Verificación
- [ ] ¿He procesado las notas de voz de esta semana?
- [ ] ¿He convertido los recortes de lectura en Notas de Ideas?
- [ ] ¿He archivado los proyectos terminados?

> [!TIP]
> **No te abrumes.** Procesar 5 minutos al día es mejor que procesar 5 horas al mes. Convierte el caos en conocimiento.
