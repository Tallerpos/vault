cp /opt/tallerpos/backups/20260725_152324/AGENTS.md /opt/tallerpos/AGENTS.md
cp /opt/tallerpos/backups/20260725_152324/.opencode.json /opt/tallerpos/.opencode.json

respecto a la base de datos, no pases clientes ni workshops a produccion, solamente hay algo de vehiculos hay vehiculos (motos) que se pone automaticamente, investiga bien, perodatos de clientes etc, no pases empezaremos de cero, analiza si hay datos necesarios que pasen a produccion investiga bien


NO se puede tocar `.env`, `docker-compose.dev.yml`, ni `docker-compose.prod.yml` (prohibido en AGENTS.md). Los TODOs quedan documentados:

- Rotar `DB_PASS`, `REDIS_PASSWORD`, `TELEGRAM_BOT_TOKEN` en prod (diferentes a dev)
- Mover passwords inline de compose a `env_file`