---
tags: config
---

# CONFIG

## 1 · Config

```space-lua
-- priority: 100
config.set("shortcuts", {
  { command = "Navigate: Home",    key = "Ctrl-Alt-h" },
  { command = "Journal: Today",    key = "Ctrl-Shift-j" },
  { command = "Quick Note",        key = "Ctrl-Shift-n" },
  { command = "Insert: Date",      key = "Ctrl-Shift-d" },
  { command = "Stats: Word Count", key = "Ctrl-Shift-w" },
})

config.set("std.widgets.toc.minHeaders", 3)
```

## 2 · Utilidades

```space-lua
-- priority: 50

function date_today()
  return os.date("%Y-%m-%d")
end

function time_now()
  return os.date("%H:%M")
end

function datetime_now()
  return os.date("%Y-%m-%d %H:%M")
end

function date_format(ts, fmt)
  fmt = fmt or "%Y-%m-%d"
  if ts > 1e10 then ts = ts / 1000 end
  return os.date(fmt, ts)
end

function word_count(text)
  local n = 0
  for _ in text:gmatch("%S+") do n = n + 1 end
  return n
end
```

## 3 · Comandos

```space-lua
-- priority: 10

command.define {
  name = "Journal: Today",
  run = function()
    local page = "Journal/" .. os.date("%Y/%m/%Y-%m-%d")
    local found = query[[
      from p = index.tag "page"
      where p.name == page
    ]]
    if #found == 0 then
      space.writePage(page,
        "---\ntags: journal\ndate: " .. os.date("%Y-%m-%d") .. "\n---\n\n" ..
        "# " .. os.date("%Y-%m-%d") .. "\n\n" ..
        "## Tareas\n- [ ] \n\n## Notas\n\n## Cierre\n\n"
      )
    end
    editor.navigate { kind = "page", page = page }
  end
}

command.define {
  name = "Quick Note",
  run = function()
    local name = editor.prompt("Nombre de la nota:")
    if not name or name == "" then return end
    local page = "Notas/" .. name
    local found = query[[
      from p = index.tag "page"
      where p.name == page
    ]]
    if #found == 0 then
      space.writePage(page,
        "---\ntags: note\ncreated: " .. datetime_now() .. "\n---\n\n# " .. name .. "\n\n"
      )
    end
    editor.navigate { kind = "page", page = page }
  end
}

command.define {
  name = "Insert: Date",
  run = function()
    local pos = editor.getCursor()
    editor.insertAtPos(pos, os.date("%Y-%m-%d"))
  end
}

command.define {
  name = "Insert: DateTime",
  run = function()
    local pos = editor.getCursor()
    editor.insertAtPos(pos, os.date("%Y-%m-%d %H:%M"))
  end
}

command.define {
  name = "Stats: Word Count",
  run = function()
    local text = editor.getText()
    local words = word_count(text)
    local lines = 0
    for _ in text:gmatch("\n") do lines = lines + 1 end
    local tt, td = 0, 0
    for _ in text:gmatch("%- %[.%]") do tt = tt + 1 end
    for _ in text:gmatch("%- %[x%]") do td = td + 1 end
    editor.flashNotification(
      string.format("Palabras: %d | Lineas: %d | Tareas: %d/%d", words, lines + 1, td, tt)
    )
  end
}

command.define {
  name = "Navigate: Home",
  run = function()
    editor.navigate { kind = "page", page = "index" }
  end
}

command.define {
  name = "Page: Duplicate",
  run = function()
    local src = editor.getCurrentPage()
    local name = editor.prompt("Nombre de la copia:")
    if not name or name == "" then return end
    local content = space.readPage(src)
    space.writePage(name, content)
    editor.flashNotification("Duplicada: " .. name)
    editor.navigate { kind = "page", page = name }
  end
}
```

## 4 · Widgets

```space-lua
-- priority: 10

function callout(tipo, titulo, contenido)
  local icon = "i"
  if tipo == "tip" then icon = "!"
  elseif tipo == "warning" then icon = "?"
  elseif tipo == "danger" then icon = "X" end
  return widget.htmlBlock(dom.div {
    class = "sb-callout sb-callout-" .. tipo,
    dom.div {
      class = "sb-callout-header",
      dom.span { class = "sb-callout-icon", icon },
      dom.strong { titulo or tipo },
    },
    dom.p { class = "sb-callout-body", contenido or "" },
  })
end

function progress(pct, label)
  pct = math.max(0, math.min(100, pct or 0))
  local color = "#ef4444"
  if pct >= 80 then color = "#22c55e"
  elseif pct >= 40 then color = "#f59e0b" end
  return widget.htmlBlock(dom.div {
    class = "sb-progress-wrap",
    dom.div {
      class = "sb-progress-header",
      dom.span { label or "Progreso" },
      dom.span { class = "sb-progress-pct", tostring(pct) .. "%" },
    },
    dom.div {
      class = "sb-progress-track",
      dom.div {
        class = "sb-progress-bar",
        style = "width:" .. pct .. "%;background:" .. color,
      },
    },
  })
end

function page_stats()
  local text = editor.getText()
  local words = word_count(text)
  local lines = 0
  for _ in text:gmatch("\n") do lines = lines + 1 end
  local tt, td = 0, 0
  for _ in text:gmatch("%- %[.%]") do tt = tt + 1 end
  for _ in text:gmatch("%- %[x%]") do td = td + 1 end
  return widget.htmlBlock(dom.div {
    class = "sb-stats-row",
    dom.div {
      class = "sb-stat",
      dom.div { class = "sb-stat-val", tostring(words) },
      dom.div { class = "sb-stat-lbl", "palabras" },
    },
    dom.div {
      class = "sb-stat",
      dom.div { class = "sb-stat-val", tostring(lines + 1) },
      dom.div { class = "sb-stat-lbl", "lineas" },
    },
    dom.div {
      class = "sb-stat",
      dom.div { class = "sb-stat-val", tostring(td) .. "/" .. tostring(tt) },
      dom.div { class = "sb-stat-lbl", "tareas" },
    },
  })
end

function recent_pages(n)
  n = n or 5
  local pages = query[[
    from p = index.tag "page"
    order by p.lastModified desc
  ]]
  local lines = {}
  local count = 0
  for _, p in ipairs(pages) do
    if count >= n then break end
    count = count + 1
    local d = ""
    if p.lastModified then
      d = " (" .. date_format(p.lastModified) .. ")"
    end
    table.insert(lines, "- [[" .. p.name .. "]]" .. d)
  end
  if #lines == 0 then
    return widget.markdownBlock("Sin paginas.")
  end
  return widget.markdownBlock(table.concat(lines, "\n"))
end

function badge(texto, color)
  color = color or "#4f98a3"
  return widget.html(dom.span {
    class = "sb-badge",
    style = "background:" .. color .. "20;color:" .. color .. ";border:1px solid " .. color .. "50",
    texto,
  })
end

function today_chip()
  return widget.html(dom.span {
    class = "sb-date-chip",
    "Hoy: " .. os.date("%d/%m/%Y"),
  })
end

function kv_table(datos)
  local rows = {}
  for _, pair in ipairs(datos) do
    table.insert(rows, dom.tr {
      dom.td { class = "sb-kv-key", tostring(pair) },
      dom.td { class = "sb-kv-val", tostring(pair) },[1]
    })
  end
  return widget.htmlBlock(dom.table {
    class = "sb-kv-table",
    dom.tbody { table.unpack(rows) },
  })
end
```

## 5 · Estilos

```space-style
.sb-callout { border-radius: 8px; padding: 10px 14px; margin: 10px 0; border: 1px solid; font-size: 0.9em; line-height: 1.55; }
.sb-callout-note    { background: oklch(65% 0.08 195 / 0.08); border-color: oklch(65% 0.08 195 / 0.3); }
.sb-callout-tip     { background: oklch(80% 0.14 80  / 0.08); border-color: oklch(80% 0.14 80  / 0.3); }
.sb-callout-warning { background: oklch(75% 0.14 60  / 0.08); border-color: oklch(75% 0.14 60  / 0.35); }
.sb-callout-danger  { background: oklch(60% 0.18 25  / 0.08); border-color: oklch(60% 0.18 25  / 0.3); }
.sb-callout-header  { display: flex; align-items: center; gap: 7px; margin-bottom: 5px; font-weight: 600; font-size: 0.92em; }
.sb-callout-note    .sb-callout-header { color: oklch(65% 0.10 195); }
.sb-callout-tip     .sb-callout-header { color: oklch(72% 0.14 80); }
.sb-callout-warning .sb-callout-header { color: oklch(68% 0.16 60); }
.sb-callout-danger  .sb-callout-header { color: oklch(58% 0.20 25); }
.sb-callout-body { color: var(--editor-secondary-text-color); margin: 0; }

.sb-progress-wrap   { margin: 6px 0 10px; }
.sb-progress-header { display: flex; justify-content: space-between; font-size: 0.82em; margin-bottom: 5px; color: var(--editor-secondary-text-color); }
.sb-progress-pct    { font-weight: 700; font-variant-numeric: tabular-nums; }
.sb-progress-track  { background: var(--editor-subtle-background-color, rgba(128,128,128,0.15)); border-radius: 999px; height: 7px; overflow: hidden; }
.sb-progress-bar    { height: 100%; border-radius: 999px; transition: width 0.35s ease; min-width: 4px; }

.sb-stats-row { display: flex; flex-wrap: wrap; gap: 10px; margin: 8px 0 12px; }
.sb-stat      { background: var(--editor-subtle-background-color, rgba(128,128,128,0.10)); border: 1px solid var(--editor-border-color, rgba(128,128,128,0.2)); border-radius: 10px; padding: 8px 18px; text-align: center; min-width: 76px; }
.sb-stat-val  { font-size: 1.25em; font-weight: 700; font-variant-numeric: tabular-nums; color: var(--editor-highlight-color, #4f98a3); line-height: 1.2; }
.sb-stat-lbl  { font-size: 0.68em; color: var(--editor-faint-text-color, rgba(128,128,128,0.7)); text-transform: uppercase; letter-spacing: 0.07em; margin-top: 3px; }

.sb-badge     { border-radius: 999px; padding: 1px 8px; font-size: 0.76em; font-weight: 600; letter-spacing: 0.03em; vertical-align: middle; }
.sb-date-chip { font-size: 0.86em; color: var(--editor-secondary-text-color); }

.sb-kv-table  { border-collapse: collapse; width: 100%; font-size: 0.88em; margin: 8px 0 12px; border: 1px solid var(--editor-border-color, rgba(128,128,128,0.2)); border-radius: 8px; overflow: hidden; }
.sb-kv-key    { padding: 6px 14px; font-weight: 600; color: var(--editor-secondary-text-color); background: var(--editor-subtle-background-color, rgba(128,128,128,0.06)); border-bottom: 1px solid var(--editor-border-color, rgba(128,128,128,0.15)); white-space: nowrap; width: 1%; }
.sb-kv-val    { padding: 6px 14px; border-bottom: 1px solid var(--editor-border-color, rgba(128,128,128,0.1)); }
.sb-kv-table tr:last-child td { border-bottom: none; }
```

---

## Referencia

| Expresion | Resultado |
|---|---|
| `${date_today()}` | `2026-04-04` |
| `${time_now()}` | `14:35` |
| `${today_chip()}` | Chip fecha |
| `${page_stats()}` | Palabras / lineas / tareas |
| `${progress(72, "Sprint 3")}` | Barra de progreso |
| `${callout("tip", "Idea", "texto")}` | Callout estilizado |
| `${badge("v2.5", "#22c55e")}` | Etiqueta de color |
| `${recent_pages(5)}` | 5 paginas recientes |
| `${kv_table({{"Clave","Valor"}})}` | Tabla clave-valor |