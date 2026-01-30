# GriPro (GridCode Project Orchestrator)

**Sistema de orquestación multi-agente para desarrollo automatizado de proyectos software con equipo de bots especializados**

## 🎯 Visión General

GriPro es un sistema de gestión de proyectos automatizado que utiliza un equipo de agentes de IA especializados ("botequipo") coordinados por un Project Manager bot (Primo) para desarrollar proyectos de software de forma autónoma, desde la especificación inicial hasta el despliegue.

## 🤖 El Botequipo

Cada bot tiene su propia personalidad, conocimiento especializado y área de responsabilidad:

### Primo (Project Manager Orchestrator)
- **Rol**: Supervisor y orquestador principal
- **Responsabilidades**:
  - Interfaz con el cliente/usuario
  - Análisis de especificaciones y contexto del proyecto
  - Planificación agile (backlog, sprints, tareas)
  - Asignación de tareas a agentes especializados
  - Control de desviaciones y calidad
  - Gestión de dependencias entre tareas

### Fronti (Frontend SEO/UX)
- **Rol**: Especialista en frontend, SEO y experiencia de usuario
- **Responsabilidades**: UI/UX, optimización SEO, accesibilidad, performance frontend

### Comi (Frontend eCommerce)
- **Rol**: Especialista en soluciones eCommerce
- **Responsabilidades**: Carrito, checkout, pasarelas de pago, catálogos

### Baky (Backend API)
- **Rol**: Arquitecto de backend y APIs
- **Responsabilidades**: Arquitectura backend, APIs REST/GraphQL, lógica de negocio

### Secu (Backend Security)
- **Rol**: Especialista en seguridad
- **Responsabilidades**: Autenticación, autorización, cifrado, auditorías de seguridad

### Qai (QA/Testing)
- **Rol**: Ingeniero de calidad
- **Responsabilidades**: Tests unitarios, integración, e2e, validación de requisitos

### Devi (DevOps/Deploy)
- **Rol**: Ingeniero de despliegue
- **Responsabilidades**: CI/CD, Docker, orquestación, monitoreo, infraestructura

### Mark (Documentation/Marketing)
- **Rol**: Documentación y comunicación
- **Responsabilidades**: Documentación técnica, user guides, contenido marketing

## 📚 Estructura del Repositorio

```
gridcode-project-orchestrator/
├── orchestrator/          # Código del orquestador (Primo)
│   ├── pm_agent/          # Lógica del Project Manager
│   ├── graph.py           # Definición del grafo LangGraph
│   └── state/             # Modelos de estado compartido
│
├── agents/                # Agentes especializados
│   ├── frontend_seo_ux/   # Fronti
│   │   ├── prompt.md
│   │   ├── knowledge/
│   │   └── config.json
│   ├── frontend_ecommerce/# Comi
│   ├── backend_api/       # Baky
│   ├── backend_security/  # Secu
│   ├── qa_tester/         # Qai
│   ├── devops_deploy/     # Devi
│   └── doc_marketing/     # Mark
│
├── data/                  # Bases de datos y estado
│   ├── agents/            # BD por agente
│   └── projects/          # Estado de proyectos
│
├── infra/                 # Infraestructura
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── hetzner/           # Scripts Hetzner
│   └── dreamhost/         # Config subdominios
│
└── docs/                  # Documentación
    ├── architecture.md
    ├── setup.md
    ├── agents-guide.md
    └── deployment.md
```

## 🚀 Flujo de Trabajo

1. **Creación de proyecto**: Se crea carpeta en Google Drive (`GRID CODE/🚀 PROJET/x REPO Y RAMAS/PROYECTO_X/`)
2. **Sync automático**: Carpeta se sincroniza con GitHub
3. **Activación de Primo**: El PM bot analiza especificaciones y contexto
4. **Planificación**: Primo genera backlog y asigna tareas a agentes
5. **Ejecución**: Agentes trabajan en paralelo/secuencia según dependencias
6. **Revisión**: Primo valida outputs de cada agente
7. **Documentación**: Mark genera docs para aprobación del cliente
8. **Despliegue**: Devi despliega a Hetzner VPS
9. **Dashboard**: Proyecto visible en `proyecto.evasoft.app`

## 🛠️ Stack Tecnológico

- **Orquestación**: LangGraph (Python)
- **LLM**: Claude API (Anthropic)
- **Repositorios**: GitHub
- **Storage**: Google Drive + GitHub
- **Hosting**: Hetzner VPS (Docker)
- **Dominios**: evasoft.app (Dreamhost)
- **CI/CD**: GitHub Actions

## 📄 Documentación de Decisiones

### Decisión 1: Monorepo único
**Fecha**: 2026-01-30  
**Contexto**: Decidimos usar un monorepo para todo el sistema (orquestador + agentes) en lugar de repos separados.  
**Razón**: Simplifica CI/CD, entorno de desarrollo y esquema mental. Facilita extraer agentes a repos propios más adelante si es necesario.  
**Estado**: Implementado

### Decisión 2: Nombres cortos para agentes
**Fecha**: 2026-01-30  
**Contexto**: Cada agente tiene un nombre técnico (carpeta) y un alias corto.  
**Razón**: Facilita referencias rápidas en conversaciones, logs y código.  
**Aliases**: Primo, Fronti, Comi, Baky, Secu, Qai, Devi, Mark  
**Estado**: Implementado

### Decisión 3: Google Drive como raíz organizativa
**Fecha**: 2026-01-30  
**Contexto**: Los proyectos nacen como carpetas en Drive y se sincronizan automáticamente con GitHub.  
**Razón**: Drive ofrece visión de negocio clara para no-desarrolladores; GitHub mantiene control de versiones técnico.  
**Estado**: Pendiente implementación

## 📌 Roadmap

- [x] Crear repositorio GitHub
- [x] Definir estructura de carpetas
- [x] Documentar arquitectura y botequipo
- [ ] Implementar Primo (PM orchestrator) con LangGraph
- [ ] Crear estructura de agentes especializados
- [ ] Configurar sync Google Drive ↔ GitHub
- [ ] Configurar CI/CD GitHub → Hetzner
- [ ] Implementar dashboard de proyectos
- [ ] Configurar subdominios en evasoft.app
- [ ] Desplegar MVP en Hetzner

## 👥 Contacto

Proyecto desarrollado por el equipo de GridCode.  
Para consultas: [Crear un issue](https://github.com/MIXWARE-REPO/gridcode-project-orchestrator/issues)

---

**Versión**: 0.1.0 (Inicialización)  
**Última actualización**: 2026-01-30
