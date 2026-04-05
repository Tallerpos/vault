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
    editor.navigate { kind = "page", page = "10_Nexo/Dashboard_Lectura" }
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
      end
    end
    editor.flashNotification("Escaneo completado. Archivos con nombres no optimos: " .. tostring(count))
  end
}
```

## Widgets

```space-lua
-- priority: 10

function recent_pages(n)
  n = n or 5
  local all = query[[from p = index.tag "page" where p.name =~ "20_Cerebro/"]]
  local sorted = {}
  for _, p in ipairs(all) do
    table.insert(sorted, { name = p.name, ts = safe_ts(p.lastModified) })
  end
  table.sort(sorted, function(a, b) return a.ts > b.ts end)
  local items = {}
  for i=1, math.min(n, #sorted) do
    table.insert(items, "- [[" .. sorted[i].name .. "]]")
  end
  return widget.new { display = "block", markdown = table.concat(items, "\n") }
end
```

## Estilos

```space-style
/* Mantener estilos existentes... */
```
