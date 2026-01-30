# Infraestructura y Despliegue GriPro

Configuración de infraestructura para el despliegue de GriPro en Hetzner VPS.

## Arquitectura de Despliegue

```
Internet
    |
Dreamhost DNS (evasoft.app)
    |
    v
Hetzner VPS "MIGRACIÓN"
    |
    +-- Docker Host
        |
        +-- GriPro Orchestrator (container)
        +-- Dashboard Web (container)
        +-- PostgreSQL / Redis (containers)
        +-- Nginx Reverse Proxy (container)
```

## Componentes

### 1. Hetzner VPS

- **Servidor**: VPS MIGRACIÓN
- **OS**: Ubuntu/Debian
- **Gestor de contenedores**: Docker + Docker Compose
- **Acceso**: SSH con clave pública

### 2. Subdominios (evasoft.app)

En Dreamhost configuraremos:

- `dev.evasoft.app` → Dashboard de desarrollo
- `api.evasoft.app` → API del orquestador
- `[proyecto].evasoft.app` → Dashboards por proyecto

**Autenticación**: Login/password por proyecto configurado en la app.

### 3. Sincronización Google Drive ↔ GitHub

**Opción 1: rclone + cron (VPS)**
```bash
# Instalar rclone en VPS
curl https://rclone.org/install.sh | sudo bash
rclone config # Configurar Google Drive

# Script sync (ejecutar cada 5 min)
rclone sync "gdrive:GRID CODE/🚀 PROJET/x REPO Y RAMAS/" /var/repos/projects/
cd /var/repos/projects/
git add .
git commit -m "Auto-sync $(date)"
git push origin main
```

**Opción 2: GitHub Workflow con secrets de Drive API**  
(Más complejo, requiere OAuth setup)

### 4. CI/CD: GitHub Actions → Hetzner

**Workflow**: `.github/workflows/deploy.yml`

```yaml
name: Deploy to Hetzner
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to VPS
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.HETZNER_IP }}
          username: root
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/gripro
            git pull origin main
            docker compose down
            docker compose up -d --build
```

**Secrets necesarios en GitHub**:
- `HETZNER_IP`
- `SSH_PRIVATE_KEY`
- `ANTHROPIC_API_KEY`
- `POSTGRES_PASSWORD`

### 5. Docker Compose

**Archivo**: `infra/docker-compose.yml`

Servicios:
- `orchestrator`: Aplicación Python LangGraph
- `dashboard`: Frontend React/Vue
- `postgres`: Base de datos
- `redis`: Caché y colas
- `nginx`: Reverse proxy

### 6. Variables de Entorno

**Archivo**: `infra/.env.example`

```env
ANTHROPIC_API_KEY=sk-ant-...
POSTGRES_DB=gripro
POSTGRES_USER=gripro
POSTGRES_PASSWORD=...
REDIS_URL=redis://redis:6379
DOMAIN=evasoft.app
```

## Estructura de Carpetas en VPS

```
/opt/gripro/
├── docker-compose.yml
├── .env
├── orchestrator/        # Código del orquestador
├── dashboard/           # Frontend
├── data/
│   ├── postgres/
│   ├── redis/
│   └── logs/
└── nginx/
    ├── nginx.conf
    └── ssl/             # Certificados Let's Encrypt
```

## Pasos de Despliegue (MVP)

### 1. Preparar VPS Hetzner

```bash
# SSH al VPS
ssh root@<HETZNER_IP>

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
sudo apt install docker-compose-plugin

# Crear estructura
mkdir -p /opt/gripro/{data/{postgres,redis,logs},nginx/ssl}
cd /opt/gripro
```

### 2. Clonar Repositorio

```bash
git clone https://github.com/MIXWARE-REPO/gridcode-project-orchestrator.git .
```

### 3. Configurar Variables

```bash
cp infra/.env.example .env
nano .env  # Editar con valores reales
```

### 4. Levantar Servicios

```bash
docker compose -f infra/docker-compose.yml up -d
```

### 5. Configurar DNS en Dreamhost

Panel Dreamhost:
- Añadir registros A:
  - `dev.evasoft.app` → `<HETZNER_IP>`
  - `api.evasoft.app` → `<HETZNER_IP>`
  - `*.evasoft.app` → `<HETZNER_IP>` (wildcard para proyectos)

### 6. SSL con Let's Encrypt

```bash
# Certbot en VPS
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d dev.evasoft.app -d api.evasoft.app
```

## Monitoreo

- **Logs**: `docker compose logs -f`
- **Status**: `docker compose ps`
- **Métricas**: Grafana + Prometheus (opcional, fase 2)

## Backups

```bash
# Script de backup automático (cron diario)
#!/bin/bash
DATE=$(date +%Y%m%d)
docker exec postgres pg_dump -U gripro gripro > /backups/gripro_$DATE.sql
# Subir a S3/Backblaze/Drive
```

## Estado

- [ ] Configurar VPS Hetzner
- [ ] Crear docker-compose.yml
- [ ] Configurar GitHub Actions workflow
- [ ] Configurar subdominios en Dreamhost
- [ ] Setup SSL
- [ ] Configurar sync Google Drive
- [ ] Implementar backups
- [ ] Desplegar MVP

---

**Responsable**: Devi (DevOps agent)  
**Última actualización**: 2026-01-30
