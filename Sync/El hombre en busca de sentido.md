---
tags: config
tipo: libro
titulo: El hombre en busca de sentido
autor: Viktor Frankl
año: 2015
editorial: Herder Editorial
idioma: ES
isbn: "9788425432033"
paginas: 125
pagina_actual: 0
portada: https://books.google.com/books/content?id=eAOIDwAAQBAJ&printsec=frontcover&img=1&fife=w400&source=gbs_api
temas:
  - Psychology
rating:
estado: leyendo
fecha_inicio: 2026-04-05
fecha_fin:
---

![El hombre en busca de sentido|200](https://books.google.com/books/content?id=eAOIDwAAQBAJ&printsec=frontcover&img=1&fife=w400&source=gbs_api)

# El hombre en busca de sentido
**Viktor Frankl** · 2015 · Herder Editorial

> *Nueva traducción* " El hombre en busca de sentido" es el estremecedor relato en el que Viktor Frankl nos narra su experiencia en los campos de concentración. Durante todos esos años de sufrimiento, sintió en su propio ser lo que significaba una existencia desnuda, absolutamente desprovista de todo, salvo de la existencia misma. Él, que todo lo había perdido, que padeció hambre, frío y brutalidades, que tantas veces estuvo a punto de ser ejecutado, pudo reconocer que, pese a todo, la vida es dig…

---

## Por qué lo leí


## Tesis principal


## Notas brutas


## Ideas clave
```dataview
LIST
FROM "20_Cerebro"
WHERE contains(fuente, this.file.name)
SORT file.ctime ASC
```

## Resumen final


## Rating y veredicto
# CONFIG

## Setup

```space-lua
-- priority: 100
config.set("std.widgets.toc.enabled", true)
config.set("std.widgets.toc.minHeaders", 3)
config.set("std.widgets.linkedMentions.enabled", true)
config.set("std.widgets.linkedTasks.enabled", true)
```

## Utilidades

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

function word_count(text)
  local n = 0
  for _ in text:gmatch("%S+") do
    n = n + 1
  end
  return n
end

function date_format(ts, fmt)
  fmt = fmt or "%Y-%m-%d"
  if ts and ts > 10000000000 then
    ts = ts / 1000
  end
  return os.date(fmt, ts)
end

function safe_ts(val)
  if type(val) == "number" then
    return val
  end
  return 0
end
```

## Comandos

```space-lua
-- priority: 10

command.define {
  name = "Go: Journal",
  run = function()
    local page = "00_Captura/Diario/" .. os.date("%Y/%m/%Y-%m-%d")
    local found = query[[from p = index.tag "page" where p.name == page]]
    if #found == 0 then
      space.writePage(
        page,
        "---\ntags: journal\ndate: "
          .. os.date("%Y-%m-%d")
          .. "\n---\n\n# "
          .. os.date("%Y-%m-%d")
          .. "\n\n## Tareas\n- [ ] \n\n## Notas\n\n## Cierre\n"
      )
    end
    editor.navigate { kind = "page", page = page }
  end
}

command.define {
  name = "Go: New Note",
  run = function()
    local name = editor.prompt("Nombre de la nota:")
    if not name or name == "" then
      return
    end
    local page = "20_Cerebro/" .. name
    space.writePage(
      page,
      "---\ntags: note\ncreated: "
        .. datetime_now()
        .. "\n---\n\n# "
        .. name
        .. "\n"
    )
    editor.navigate { kind = "page", page = page }
  end
}

command.define {
  name = "Go: Home",
  run = function()
    editor.navigate { kind = "page", page = "index" }
  end
}

command.define {
  name = "Stats: Words",
  run = function()
    local text = editor.getText()
    local words = word_count(text)
    local lines = 0
    local total = 0
    local done = 0
    for _ in text:gmatch("\n") do
      lines = lines + 1
    end
    for _ in text:gmatch("%- %[.%]") do
      total = total + 1
    end
    for _ in text:gmatch("%- %[x%]") do
      done = done + 1
    end
    editor.flashNotification(
      string.format("Palabras: %d | Lineas: %d | Tareas: %d/%d", words, lines + 1, done, total)
    )
  end
}

command.define {
  name = "Sistema: Sanear Boveda",
  run = function()
    local all = query[[from p = index.tag "page"]]
    local count = 0
    for _, p in ipairs(all) do
      if p.name:match("[%s%z\1-\31]") then
        count = count + 1
        -- Solo notificamos por ahora para evitar cambios destructivos sin supervision
      end
    end
    editor.flashNotification("Escaneo completado. Archivos con nombres no optimos encontrados: " .. tostring(count))
  end
}
```

## Slash Commands

```space-lua
-- priority: 10

slashCommand.define {
  name = "date",
  run = function()
    editor.insertAtCursor(os.date("%Y-%m-%d"))
  end
}

slashCommand.define {
  name = "time",
  run = function()
    editor.insertAtCursor(os.date("%H:%M"))
  end
}

slashCommand.define {
  name = "datetime",
  run = function()
    editor.insertAtCursor(os.date("%Y-%m-%d %H:%M"))
  end
}

slashCommand.define {
  name = "todo",
  run = function()
    editor.insertAtCursor("- [ ] ")
  end
}

slashCommand.define {
  name = "done",
  run = function()
    editor.insertAtCursor("- [x] ")
  end
}

slashCommand.define {
  name = "hr",
  run = function()
    editor.insertAtCursor("\n\n---\n\n")
  end
}

slashCommand.define {
  name = "journal",
  run = function()
    editor.invokeCommand("Go: Journal")
  end
}

slashCommand.define {
  name = "newnote",
  run = function()
    editor.invokeCommand("Go: New Note")
  end
}

slashCommand.define {
  name = "stats",
  run = function()
    editor.invokeCommand("Stats: Words")
  end
}
```

## Botones

```space-lua
-- priority: 10

function sb_btn(text, cmd)
  return widget.html(dom.button {
    class = "sb-btn",
    onclick = function()
      editor.invokeCommand(cmd)
    end,
    text
  })
end

function sb_btn_primary(text, cmd)
  return widget.html(dom.button {
    class = "sb-btn sb-btn-primary",
    onclick = function()
      editor.invokeCommand(cmd)
    end,
    text
  })
end
```

## Widgets

```space-lua
-- priority: 10

function progress(pct, label)
  pct = math.max(0, math.min(100, pct or 0))
  local color = "#ef4444"
  if pct >= 80 then
    color = "#22c55e"
  elseif pct >= 40 then
    color = "#f59e0b"
  end
  return widget.new {
    display = "block",
    html = "<div class=\"sb-pw\">"
      .. "<div class=\"sb-ph\">"
      .. "<span>" .. (label or "Progreso") .. "</span>"
      .. "<span class=\"sb-pp\">" .. tostring(pct) .. "%</span>"
      .. "</div>"
      .. "<div class=\"sb-pt\">"
      .. "<div class=\"sb-pb\" style=\"width:" .. tostring(pct) .. "%;background:" .. color .. ";\"></div>"
      .. "</div>"
      .. "</div>"
  }
end

function page_stats()
  local text = editor.getText()
  local words = word_count(text)
  local lines = 0
  local total = 0
  local done = 0
  for _ in text:gmatch("\n") do
    lines = lines + 1
  end
  for _ in text:gmatch("%- %[.%]") do
    total = total + 1
  end
  for _ in text:gmatch("%- %[x%]") do
    done = done + 1
  end
  return widget.new {
    display = "block",
    html = "<div class=\"sb-sr\">"
      .. "<div class=\"sb-st\"><div class=\"sb-sv\">" .. tostring(words) .. "</div><div class=\"sb-sl\">palabras</div></div>"
      .. "<div class=\"sb-st\"><div class=\"sb-sv\">" .. tostring(lines + 1) .. "</div><div class=\"sb-sl\">lineas</div></div>"
      .. "<div class=\"sb-st\"><div class=\"sb-sv\">" .. tostring(done) .. "/" .. tostring(total) .. "</div><div class=\"sb-sl\">tareas</div></div>"
      .. "</div>"
  }
end

function recent_pages(n)
  n = n or 5
  local all = query[[from p = index.tag "page"]]
  local sorted = {}
  for _, p in ipairs(all) do
    table.insert(sorted, {
      name = p.name,
      ts = safe_ts(p.lastModified)
    })
  end
  table.sort(sorted, function(a, b)
    return a.ts > b.ts
  end)
  local items = {}
  local count = 0
  for _, p in ipairs(sorted) do
    if count >= n then
      break
    end
    count = count + 1
    local extra = ""
    if p.ts > 0 then
      extra = " (" .. date_format(p.ts) .. ")"
    end
    table.insert(items, "- [[" .. p.name .. "]]" .. extra)
  end
  if #items == 0 then
    return widget.new { display = "block", markdown = "Sin paginas." }
  end
  return widget.new { display = "block", markdown = table.concat(items, "\n") }
end

function recent_journal(n)
  n = n or 5
  local all = query[[from p = index.tag "journal"]]
  local sorted = {}
  for _, p in ipairs(all) do
    table.insert(sorted, {
      name = p.name,
      ts = safe_ts(p.lastModified)
    })
  end
  table.sort(sorted, function(a, b)
    return a.ts > b.ts
  end)
  local items = {}
  local count = 0
  for _, p in ipairs(sorted) do
    if count >= n then
      break
    end
    count = count + 1
    table.insert(items, "- [[" .. p.name .. "]]")
  end
  if #items == 0 then
    return widget.new { display = "block", markdown = "Sin entradas de diario." }
  end
  return widget.new { display = "block", markdown = table.concat(items, "\n") }
end
```

## Estilos

```space-style
.sb-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 16px;
  border-radius: 8px;
  border: 1px solid var(--editor-border-color, rgba(128,128,128,.3));
  background: var(--editor-subtle-background-color, rgba(128,128,128,.1));
  color: var(--editor-text-color, inherit);
  font-size: 0.88em;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.15s ease;
  margin: 2px;
  text-decoration: none;
}

.sb-btn:hover {
  background: #0ea5e9;
  border-color: #0ea5e9;
  color: #fff;
  box-shadow: 0 2px 10px rgba(14,165,233,.35);
}

.sb-btn-primary {
  background: #0ea5e9;
  border-color: #0ea5e9;
  color: #fff;
  box-shadow: 0 2px 8px rgba(14,165,233,.25);
}

.sb-btn-primary:hover {
  background: #0284c7;
  border-color: #0284c7;
  box-shadow: 0 3px 14px rgba(14,165,233,.4);
}

.sb-sr {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin: 10px 0 16px;
}

.sb-st {
  background: var(--editor-subtle-background-color, rgba(128,128,128,.1));
  border: 1px solid var(--editor-border-color, rgba(128,128,128,.18));
  border-radius: 12px;
  padding: 10px 20px;
  text-align: center;
  min-width: 96px;
}

.sb-sv {
  font-size: 1.35em;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: #0ea5e9;
  line-height: 1.15;
}

.sb-sl {
  font-size: 0.68em;
  color: var(--editor-faint-text-color, rgba(128,128,128,.7));
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-top: 4px;
}

.sb-pw {
  margin: 8px 0 14px;
  padding: 12px 14px;
  background: var(--editor-subtle-background-color, rgba(128,128,128,.08));
  border: 1px solid var(--editor-border-color, rgba(128,128,128,.18));
  border-radius: 12px;
}

.sb-ph {
  display: flex;
  justify-content: space-between;
  font-size: 0.84em;
  margin-bottom: 8px;
  color: var(--editor-secondary-text-color, rgba(128,128,128,.8));
}

.sb-pp {
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.sb-pt {
  background: rgba(148,163,184,.2);
  border-radius: 999px;
  height: 9px;
  overflow: hidden;
}

.sb-pb {
  height: 100%;
  border-radius: 999px;
  transition: width 0.4s ease;
  min-width: 4px;
}
```