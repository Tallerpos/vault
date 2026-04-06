# 🗺️ Mapa de Conexiones (Tu Inteligencia Viva)

Este archivo es el "GPS" de tu Segundo Cerebro. Se actualiza solo y te dice dónde hay huecos en tu conocimiento.

---

## 🧭 Grandes Temas (Ejes Centrales)
*Estos son tus pilares. Cuantas más notas tengan, más dominas el tema.*

```dataview
TABLE length(file.inlinks) as "Conexiones", length(file.outlinks) as "Referencias"
FROM "TEMAS"
WHERE file.name != "Dashboard_Lectura"
SORT length(file.inlinks) DESC
```

---

## 🧩 Ideas "Semilla" (Sin Conexión)
*Estas son notas en tu carpeta `NOTAS` que no están enlazadas a ningún Tema. ¡Conéctalas para que no se pierdan!*

```dataview
LIST
FROM "NOTAS"
WHERE length(file.inlinks) = 0
```

---

## 🔥 Libros más Influyentes
*Los libros que más ideas te han inspirado.*

```dataview
TABLE length(file.inlinks) as "Ideas Generadas"
FROM "BIBLIOTECA/Libros"
SORT length(file.inlinks) DESC
LIMIT 5
```

---

## 🚀 Proyectos en Marcha
*Lo que estás haciendo ahora mismo.*

```dataview
LIST
FROM "PROYECTOS"
WHERE !contains(file.name, "Mantenimiento")
```

---

> [!TIP]
> **Cómo usar este mapa:** 
> Si ves algo en **Ideas Semilla**, abre esa nota e intenta enlazarla a uno de tus **Grandes Temas**. Así es como tu cerebro se vuelve más inteligente: forzando conexiones.
