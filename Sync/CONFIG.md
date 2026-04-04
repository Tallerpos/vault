-- priority: 100
config.set {
  -- ─── Plugs ──────────────────────────────────────────────────────────
  -- Descomenta los que quieras activar.
  plugs = {
    -- "github:silverbulletmd/silverbullet-git/git.plug.js",
    -- "github:silverbulletmd/silverbullet-ai/ai.plug.js",
  },

  -- ─── Atajos de teclado ──────────────────────────────────────────────
  shortcuts = {
    { command = "Navigate: Home",    key = "Ctrl-Alt-h" },
    { command = "Journal: Today",    key = "Ctrl-Shift-j" },
    { command = "Quick Note",        key = "Ctrl-Shift-n" },
    { command = "Insert: Date",      key = "Ctrl-Shift-d" },
    { command = "Stats: Word Count", key = "Ctrl-Shift-w" },
    -- { command = "Git: Sync",      key = "Ctrl-Alt-." },
  },

  -- ─── Sync (si usas Git plug) ─────────────────────────────────────────
  -- git = {
  --   autoSync  = true,
  --   syncOnSave = true,
  -- },
}