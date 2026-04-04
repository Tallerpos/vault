# 📘 Documentación Completa del Sistema Obsidian Sync

Este archivo contiene toda la información necesaria para entender, administrar o reconstruir este sistema desde cero.

---

## 🏗️ Arquitectura General
El sistema utiliza una arquitectura de **3 capas**:
1.  **Almacenamiento y Sincronización (WebDAV)**: Permite que Obsidian (PC/Móvil) lea y escriba archivos.
2.  **Interfaz Web (SilverBullet)**: Permite editar las notas desde cualquier navegador en `https://git.paginox.com`.
3.  **Respaldo Automático (Git Watcher)**: Un script vigila los cambios en el VPS y los sube a GitHub al instante.

---

## 📂 Directorios y Rutas Críticas
-   **/opt/obsidian-sync/**: Carpeta principal del proyecto (Docker).
-   **/opt/vault/**: Tu bóveda de Obsidian.
    -   **/opt/vault/Sync/**: Tus notas reales.
    -   **/opt/vault/Sync/SISTEMA/**: Este reporte y documentación.
-   **/opt/vault-watcher.sh**: Script de respaldo a GitHub.
-   **/opt/obsidian-intelligence.sh**: Script de inteligencia (Tareas, Dashboard).

---

## �� Servicios Docker (`/opt/obsidian-sync/docker-compose.yml`)
-   **obsidian-webdav**: Puerto `1293`. Servidor WebDAV ligero.
-   **obsidian-silverbullet**: Puerto `1294`. Editor Markdown extensible.
-   **obsidian-watchtower**: Actualiza automáticamente WebDAV y SilverBullet cada 24h.

**Credenciales Únicas:**
-   **Usuario**: `abner`
    -   **Contraseña**: `TiWBaVKTTAEyw8JE`

---

## 🔄 Servicios del Sistema (systemd)
Si necesitas reiniciar algún proceso manual:
-   `sudo systemctl restart vault-watcher`: Reinicia el respaldo a GitHub.
-   `sudo systemctl restart obsidian-intelligence.timer`: Reinicia los reportes automáticos.

---

## 🛠️ Cómo Reconstruir el Proyecto (Disaster Recovery)
Si el VPS se borrara y quieres volver a montar todo:
1.  **Instalar Docker e inotify-tools**: `sudo apt install docker.io docker-compose inotify-tools`.
2.  **Clonar tu Bóveda**: `git clone https://github.com/Tallerpos/vault.git /opt/vault`.
3.  **Crear el Docker Compose**: Usa el contenido de `/opt/obsidian-sync/docker-compose.yml`.
4.  **Reinstalar Scripts**: Copia `/opt/vault-watcher.sh` y `/opt/obsidian-intelligence.sh` a `/opt/`.
5.  **Activar Servicios**: Crea los archivos `.service` en `/etc/systemd/system/` y haz `systemctl enable --now`.

---

## 🤖 Suite de Inteligencia
-   **Dashboard.md**: Estado global en tiempo real.
-   **Tareas_Pendientes.md**: Recopilación de todos tus `- [ ]` en la bóveda.
-   **Integridad.md**: Reporte de enlaces rotos y sugerencias.

*Este sistema ha sido diseñado para ser Robusto, Seguro y Cero Mantenimiento.*
