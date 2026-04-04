---
tags: config
---

# CONFIG

## Setup

```space-lua
-- priority: 100
config.set("std.widgets.toc.enabled", true)
config.set("std.widgets.toc.minHeaders", 3)
config.set("std.widgets.linkedMentions.enabled", true)
config.set("std.widgets.linkedTasks.enabled", true)
```

## Utils

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
  if ts > 10000000000 then
    ts = ts / 1000
  end
  return os.date(fmt, ts)
end
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
    local page = "Journal/" .. os.date("%Y/%m/%Y-%m-%d")
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

slashCommand.define {
  name = "newnote",
  run = function()
    local name = editor.prompt("Nombre de la nota:")
    if not name or name == "" then
      return
    end
    local page = "Notas/" .. name
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

slashCommand.define {
  name = "stats",
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
  local pages = query[[from p = index.tag "page" order by p.lastModified desc]]
  local items = {}
  local count = 0

  for _, p in ipairs(pages) do
    if count >= n then
      break
    end
    count = count + 1
    local extra = ""
    if p.lastModified then
      extra = " (" .. date_format(p.lastModified) .. ")"
    end
    table.insert(items, "- [[" .. p.name .. "]]" .. extra)
  end

  if #items == 0 then
    return widget.new {
      display = "block",
      markdown = "Sin paginas."
    }
  end

  return widget.new {
    display = "block",
    markdown = table.concat(items, "\n")
  }
end
```

## Style

```space-style
html {
  --ui-accent-color: #0ea5e9;
  --editor-width: 980px !important;
  --editor-font: "Inter", "Segoe UI", sans-serif !important;
}

html[data-theme="dark"] {
  --ui-accent-color: #38bdf8;
}

#sb-top {
  background: linear-gradient(90deg, #f8fafc, #eef6ff) !important;
  border-bottom: 1px solid rgba(14, 165, 233, 0.15) !important;
}

html[data-theme="dark"] #sb-top {
  background: linear-gradient(90deg, #0f172a, #111827) !important;
  border-bottom: 1px solid rgba(56, 189, 248, 0.18) !important;
}

.cm-editor .cm-content {
  line-height: 1.7;
}

.sb-sr {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin: 10px 0 16px;
}

.sb-st {
  background: var(--editor-subtle-background-color, rgba(128,128,128,0.10));
  border: 1px solid var(--editor-border-color, rgba(128,128,128,0.18));
  border-radius: 12px;
  padding: 10px 20px;
  text-align: center;
  min-width: 96px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.sb-sv {
  font-size: 1.35em;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: var(--ui-accent-color, #0ea5e9);
  line-height: 1.15;
}

.sb-sl {
  font-size: 0.68em;
  color: var(--editor-faint-text-color, rgba(128,128,128,0.7));
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-top: 4px;
}

.sb-pw {
  margin: 8px 0 14px;
  padding: 10px 12px;
  background: var(--editor-subtle-background-color, rgba(128,128,128,0.08));
  border: 1px solid var(--editor-border-color, rgba(128,128,128,0.14));
  border-radius: 12px;
}

.sb-ph {
  display: flex;
  justify-content: space-between;
  font-size: 0.84em;
  margin-bottom: 8px;
  color: var(--editor-secondary-text-color);
}

.sb-pp {
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.sb-pt {
  background: rgba(148,163,184,0.18);
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

.sb-hashtag[data-tag-name] {
  border-radius: 999px;
  padding: 1px 8px;
}
```

## Uso

Escribe `/` en cualquier pagina para ver estos comandos:

- `/date`
- `/time`
- `/datetime`
- `/todo`
- `/done`
- `/hr`
- `/journal`
- `/newnote`
- `/stats`

## Demo

${page_stats()}

${progress(62, "Configuracion")}

### Paginas recientes

${recent_pages(5)}