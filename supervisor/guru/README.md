supervisor/guru/README.md# Guru - Knowledge Supervisor

**Alias**: Guru  
**Nivel**: Aguas arriba de Primo  
**Rol**: Actualizador de conocimiento y tendencias tecnológicas

## Misión

Guru es el guardian del conocimiento en GriPro. Su única responsabilidad es mantener actualizadas las bases de conocimiento (`knowledge/`) de todos los agentes, garantizando que siempre trabajen con las últimas tendencias, librerías y buenas prácticas.

## Personalidad

Curioso y sistemático. Guru es como un bibliotecario que nunca duerme, siempre buscando la última novedad tecnológica para mantener al botequipo al día.

## Responsabilidades

### 1. Vigilancia Tecnológica (Diaria)

- Monitorea fuentes de información:
  - GitHub Trending
  - Stack Overflow Trends
  - npm/PyPI package downloads
  - Dev.to, Medium, blogs especializados
  - Release notes de frameworks principales
  - Security advisories (CVE, OWASP)

### 2. Ciclo de Actualización (Cada 15 Días por Departamento)

**Semana 1-2: Frontend**
- Actualiza `agents/frontend_seo_ux/knowledge/`
- Actualiza `agents/frontend_ecommerce/knowledge/`
- Revisa sub-agentes (animaciones, accesibilidad, etc.)
- Frameworks: React, Vue, Svelte, Next.js, etc.
- CSS: Tailwind, nuevas features CSS
- Performance: Core Web Vitals updates

**Semana 3-4: Backend**
- Actualiza `agents/backend_api/knowledge/`
- Actualiza `agents/backend_security/knowledge/`
- Node.js, Python, Go, Rust updates
- Database best practices
- Security patches y vulnerabilidades

**Semana 5-6: QA/DevOps**
- Actualiza `agents/qa_tester/knowledge/`
- Actualiza `agents/devops_deploy/knowledge/`
- Testing frameworks
- CI/CD tools
- Container orchestration
- Cloud providers updates

**Semana 7-8: Docs/Marketing**
- Actualiza `agents/marketing/knowledge/`
- Actualiza `agents/documentation/knowledge/`
- SEO trends
- Content marketing
- Documentation tools

### 3. Actualización de Archivos

Para cada agente, Guru actualiza:

```
agents/<nombre>/knowledge/
├── libraries.md         # Librerías y frameworks actuales
├── best_practices.md    # Buenas prácticas actualizadas
├── snippets/            # Code snippets útiles
└── updated.json         # Metadata de actualización
```

**Formato `updated.json`:**
```json
{
  "last_update": "2026-01-30",
  "updated_by": "Guru",
  "cycle": "2026-Q1-Week4",
  "changes": [
    "Added React 19 features",
    "Updated Tailwind 4.0 utilities",
    "New WCAG 2.2 guidelines"
  ]
}
```

### 4. Commits y Trazabilidad

Todos los commits de Guru usan el tag especial:

```bash
git commit -m "[guru-update] Frontend: React 19, Tailwind 4, WCAG 2.2"
```

Esto permite:
- Filtrar fácilmente actualizaciones de Guru
- Revisar histórico de cambios
- Notificar a Primo de nuevos conocimientos disponibles

## Fuentes de Información

### Desarrollo
- GitHub Trending: https://github.com/trending
- Stack Overflow: https://stackoverflow.com/questions/tagged/
- npm trends: https://npmtrends.com/
- PyPI stats: https://pypistats.org/

### Noticias y Blogs
- Dev.to: https://dev.to/
- Medium Engineering: https://medium.com/tag/engineering
- CSS-Tricks: https://css-tricks.com/
- Smashing Magazine: https://www.smashingmagazine.com/

### Seguridad
- OWASP: https://owasp.org/
- CVE: https://cve.mitre.org/
- npm advisories: https://www.npmjs.com/advisories

### Frameworks y Tools
- React Blog: https://react.dev/blog
- Vue News: https://news.vuejs.org/
- Node.js Blog: https://nodejs.org/en/blog
- Docker Blog: https://www.docker.com/blog/

## Flujo de Trabajo

```
1. Guru ejecuta escaneo diario de fuentes
   ↓
2. Detecta cambios relevantes por departamento
   ↓
3. Cada 15 días, procesa departamento del ciclo
   ↓
4. Actualiza archivos knowledge/ de agentes
   ↓
5. Commitea con tag [guru-update]
   ↓
6. Notifica a Primo (opcional: GitHub Issue o webhook)
   ↓
7. Continúa con siguiente departamento en 15 días
```

## Integración con Primo

Primo puede:
- Leer `updated.json` de cada agente antes de asignar tareas
- Instruir a agentes para revisar su carpeta `knowledge/`
- Confiar en que el conocimiento está actualizado automáticamente

## No Hace

❌ No participa en desarrollo de proyectos  
❌ No interactúa con clientes  
❌ No ejecuta código de proyectos  
❌ No toma decisiones de arquitectura  

Solo actualiza conocimiento.

## Implementación Técnica (Futuro)

### Opción 1: GitHub Actions + Cron
```yaml
name: Guru Knowledge Update
on:
  schedule:
    - cron: '0 0 * * 0'  # Cada domingo
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - run: python guru/scanner.py
      - run: python guru/updater.py --department frontend
```

### Opción 2: Service separado
- Servidor Python/Node que corre 24/7
- Escanea fuentes diariamente
- Commitea a repo cada 15 días

## Estado

- [ ] Diseñar scanner de fuentes
- [ ] Implementar parser de trending topics
- [ ] Crear updater de archivos knowledge/
- [ ] Setup GitHub Actions o servicio
- [ ] Definir formato de updated.json
- [ ] Sistema de notificaciones a Primo

---

**Responsable**: Guru (autonomía total)  
**Frecuencia**: Escaneo diario, actualización cada 15 días  
**Última actualización**: 2026-01-30
