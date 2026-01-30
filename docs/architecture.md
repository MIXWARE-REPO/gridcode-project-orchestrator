docs/architecture.md# Arquitectura GriPro - Sistema Multi-Agente

## Jerarquía de Agentes

```
GURU (Supervisor Global)
    |
    v (actualiza conocimiento cada 15 días)
    |
PRIMO (Project Manager)
    |
    +-- Botequipo Especializado
        |
        +-- FRONTI (Frontend SEO/UX)
        +-- COMI (Frontend eCommerce)
        +-- BAKY (Backend API)
        +-- SECU (Backend Security)
        +-- QAI (QA/Testing)
        +-- DEVI (DevOps/Deploy)
        +-- MARK (Marketing)
        +-- DOCU (Documentación de Proyectos)
```

## Nivel 1: GURU - Supervisor de Conocimiento

**Alias**: Guru  
**Carpeta**: `supervisor/guru/`  
**Nivel**: Aguas arriba de Primo  
**Rol**: Actualizador de conocimiento y tendencias

### Responsabilidades

- **Vigilancia tecnológica**: Monitorea tendencias del mercado cada semana
- **Actualización de bases de conocimiento**: Actualiza knowledge bases de todos los agentes cada 15 días
- **Ciclo semanal rotativo**: Cada semana se enfoca en un departamento diferente
  - Semana 1: Frontend (Fronti, Comi, sub-agentes)
  - Semana 2: Backend (Baky, Secu)
  - Semana 3: QA/DevOps (Qai, Devi)
  - Semana 4: Docs/Marketing (Mark, Docu)
- **Actualización de lineamientos**: Librerías, frameworks, buenas prácticas
- **Acceso a repositorios**: Lee y actualiza archivos `knowledge/` de cada agente
- **Sin intervención en proyectos**: No participa en desarrollo, solo mantiene conocimiento actualizado

### Fuentes de Información

- GitHub Trending
- Stack Overflow Trends
- npm/PyPI package stats
- Dev.to, Medium, blogs especializados
- Release notes de frameworks principales
- Security advisories (CVE, OWASP)

### Flujo de Actualización
```
1. Guru escanea fuentes (diario)
2. Detecta cambios relevantes por departamento
3. Cada 15 días, actualiza knowledge/ del departamento en turno
4. Commitea cambios al repo con tag [guru-update]
5. Notifica a Primo de actualizaciones disponibles
```

---

## Nivel 2: PRIMO - Project Manager Orchestrator

**Alias**: Primo  
**Carpeta**: `orchestrator/pm_agent/`  
**Nivel**: Coordinador del botequipo  
**Rol**: Gestión de proyectos y coordinación

### Responsabilidades

- Recibe proyectos nuevos
- Lee conocimiento actualizado por Guru
- Planifica y asigna tareas
- Coordina ejecución del botequipo
- Interface con el cliente

---

## Nivel 3: Botequipo Especializado

### Departamento Frontend

#### FRONTI - Frontend SEO/UX Lead
**Carpeta**: `agents/frontend_seo_ux/`  
**Sub-agentes potenciales**:
- `agents/frontend_seo_ux/sub_agents/animations/` - Especialista en animaciones CSS/JS
- `agents/frontend_seo_ux/sub_agents/accessibility/` - Especialista WCAG

Responsabilidades: UI/UX, SEO, performance, accesibilidad

#### COMI - Frontend eCommerce Specialist
**Carpeta**: `agents/frontend_ecommerce/`  
**Sub-agentes potenciales**:
- Checkout flows
- Product catalogs
- Payment integrations

Responsabilidades: Soluciones eCommerce completas

---

### Departamento Backend

#### BAKY - Backend API Architect
**Carpeta**: `agents/backend_api/`  
**Sub-agentes potenciales**:
- API design (REST/GraphQL)
- Database optimization
- Microservices

Responsabilidades: Arquitectura backend, APIs, integraciones

#### SECU - Backend Security Specialist
**Carpeta**: `agents/backend_security/`  
**Sub-agentes potenciales**:
- Auth (JWT, OAuth)
- Encryption
- Vulnerability scanning

Responsabilidades: Seguridad, autenticación, autorización

---

### Departamento QA/DevOps

#### QAI - QA/Testing Engineer
**Carpeta**: `agents/qa_tester/`  
**Sub-agentes potenciales**:
- Unit testing
- E2E testing
- Performance testing

Responsabilidades: Testing completo, validación

#### DEVI - DevOps/Deploy Engineer
**Carpeta**: `agents/devops_deploy/`  
**Sub-agentes potenciales**:
- CI/CD pipelines
- Container orchestration
- Monitoring

Responsabilidades: Despliegue, infraestructura, monitoreo

---

### Departamento Comunicación

#### MARK - Marketing & Communication
**Carpeta**: `agents/marketing/`  
**Sub-agentes potenciales**:
- SEO content
- Social media
- Email campaigns

Responsabilidades: Marketing, comunicación externa

#### DOCU - Project Documentation Specialist
**Alias**: Docu  
**Carpeta**: `agents/documentation/`  
**Rol**: Documentador interno de proyectos (no externo como Mark)

**Responsabilidades**:
- Documentación técnica de proyectos en desarrollo
- READMEs de proyectos específicos
- Diagramas de arquitectura
- Guías de contribución
- Changelog y release notes
- Documentación de APIs internas

**Diferencia con Mark**: Docu documenta el proyecto desde dentro (para devs), Mark crea contenido hacia fuera (para usuarios/clientes).

---

## Ciclo de Vida de Conocimiento

### Actualización Semanal (Guru)

```
Semana 1: Frontend
  - Actualiza knowledge de Fronti
  - Actualiza knowledge de Comi
  - Actualiza sub-agentes de animaciones, etc.

Semana 2: Backend
  - Actualiza knowledge de Baky
  - Actualiza knowledge de Secu

Semana 3: QA/DevOps
  - Actualiza knowledge de Qai
  - Actualiza knowledge de Devi

Semana 4: Docs/Marketing
  - Actualiza knowledge de Mark
  - Actualiza knowledge de Docu

(Repite ciclo)
```

### Estructura de Knowledge por Agente

Cada agente tiene:

```
agents/<nombre>/
├── README.md              # Definición del agente
├── prompt.md              # Prompt base
├── config.json            # Configuración
├── knowledge/
│   ├── libraries.md       # Librerías actualizadas por Guru
│   ├── best_practices.md  # Buenas prácticas actualizadas
│   ├── snippets/          # Code snippets útiles
│   └── updated.json       # Metadata de última actualización
└── sub_agents/            # (opcional) Agentes especializados
```

---

## Escalabilidad

### Añadir Sub-Agentes

Cuando un dominio crece:

```
agents/frontend_seo_ux/sub_agents/animations/
agents/frontend_seo_ux/sub_agents/accessibility/
agents/backend_api/sub_agents/graphql/
```

Guru también los actualiza en su ciclo semanal.

### Añadir Nuevos Departamentos

Si necesitas:
- Mobile (React Native, Flutter)
- Data Science (ML models)
- Blockchain

Se añaden al ciclo de Guru (extendiendo a 5-6 semanas).

---

## Ventajas de esta Arquitectura

✅ **Conocimiento siempre actualizado**: Guru mantiene todo al día  
✅ **Escalabilidad**: Fácil añadir sub-agentes  
✅ **Separación de concerns**: Cada agente tiene área clara  
✅ **Autonomia**: Primo no necesita preocuparse por actualizaciones  
✅ **Trazabilidad**: Commits de Guru con tag `[guru-update]`  

---

**Fecha**: 2026-01-30  
**Versión**: 1.0.0
