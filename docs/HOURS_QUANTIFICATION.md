# Sistema de Cuantificacion Horaria - GriPro

## Resumen Ejecutivo

Este documento establece la metodologia oficial para cuantificar las horas de trabajo dedicadas a cada proyecto por el equipo de desarrollo de GriPro. El sistema se basa en metricas de productividad de software ampliamente documentadas en la industria.

---

## 1. Fundamento Teorico

### 1.1 Metricas de Productividad en Desarrollo de Software

La cuantificacion de horas se basa en estudios empiricos sobre lineas de codigo (LOC) por unidad de tiempo:

| Fuente | Metrica | Contexto |
|--------|---------|----------|
| Fred Brooks, "The Mythical Man-Month" (1975) | ~10 LOC/dia | Proyectos OS/360, IBM |
| Capers Jones, "Applied Software Measurement" | 8-16 LOC/dia | Software embebido confiable |
| Steve McConnell, "Code Complete" | 10-50 LOC/dia | Proyectos comerciales |
| Estudios empiricos modernos | 20-100 LOC/dia util | Promedio ~40-60 LOC/dia |

### 1.2 Calculo Base

**Premisa fundamental:** En una jornada de 8 horas laborales, solo ~4 horas son de codificacion pura (el resto incluye reuniones, planificacion, debugging, etc.).

**Formula base:**
```
4 horas de trabajo efectivo = 100 lineas de codigo neto
Ratio: 1 hora = 25 LOC
```

### 1.3 Referencias Academicas y Profesionales

1. **Brooks, F.P. (1975).** "The Mythical Man-Month: Essays on Software Engineering." Addison-Wesley.
   - Establece ~10 LOC/dia como metrica para proyectos grandes.

2. **Jones, C. (2008).** "Applied Software Measurement: Global Analysis of Productivity and Quality." McGraw-Hill.
   - Rangos de 1.5-125 LOC/dia segun complejidad.
   - Promedio industria: 10-20 LOC/dia.

3. **McConnell, S. (2004).** "Code Complete: A Practical Handbook of Software Construction." Microsoft Press.
   - Productividad varia 10x entre desarrolladores.
   - Codigo "neto" (despues de ediciones) es la metrica valida.

4. **Experiencias practicas documentadas:**
   - Better Embedded SW Blog
   - La Naturaleza del Software (analisis hispanohablante)
   - Discusiones Stack Overflow/Reddit con datos reales

---

## 2. Sistema de Niveles de Especializacion

### 2.1 Estructura Jerarquica

```
Nivel 1: Departamentos Genericos
    |
    +-- Nivel 2: Especialistas Departamentales
            |
            +-- Nivel 3: Sub-especialistas
```

### 2.2 Definicion de Niveles

#### Nivel 1 - Departamentos Genericos
**Ratio: 2 horas por cada 50 lineas o fraccion**

| Departamento | Codigo | Descripcion |
|--------------|--------|-------------|
| Frontend Development | fronti_frontend | Desarrollo UI general |
| Backend Development | baky_backend | APIs y logica de servidor |
| DevOps & Infrastructure | devi_devops | CI/CD, deployment |
| Quality Assurance | qai_testing | Testing general |
| Security & Compliance | secu_security | Seguridad basica |
| Documentation | mark_marketing | Documentacion tecnica |

#### Nivel 2 - Especialistas Departamentales
**Ratio: 2 horas por cada 30 lineas o fraccion**

| Especialista | Departamento Padre | Descripcion |
|--------------|-------------------|-------------|
| UX Designer | Frontend | Experiencia de usuario |
| UI Designer | Frontend | Interfaces visuales |
| API Architect | Backend | Diseno de APIs |
| Database Engineer | Backend | Optimizacion BD |
| Security Auditor | Security | Auditorias especializadas |
| Performance Engineer | DevOps | Optimizacion rendimiento |
| Test Automation | QA | Automatizacion de pruebas |

#### Nivel 3 - Sub-especialistas
**Ratio: 2 horas por cada 20 lineas o fraccion**

| Sub-especialista | Especialista Padre | Descripcion |
|------------------|-------------------|-------------|
| SEO Specialist | UX Designer | Optimizacion buscadores |
| Animation Expert | UI Designer | Animaciones complejas |
| Accessibility Expert | UX Designer | WCAG compliance |
| GraphQL Specialist | API Architect | APIs GraphQL |
| Real-time Specialist | Backend | WebSockets, eventos |
| Penetration Tester | Security Auditor | Testing de seguridad |
| Mobile Performance | Performance | Optimizacion mobile |

### 2.3 Tabla de Conversion Rapida

| Nivel | Lineas | Horas | Ratio |
|-------|--------|-------|-------|
| 1 | 50 | 2 | 25 LOC/h |
| 1 | 100 | 4 | 25 LOC/h |
| 2 | 30 | 2 | 15 LOC/h |
| 2 | 60 | 4 | 15 LOC/h |
| 3 | 20 | 2 | 10 LOC/h |
| 3 | 40 | 4 | 10 LOC/h |

---

## 3. Horas de Coordinacion

### 3.1 Reuniones de Traspaso de Requerimientos

Cada vez que Primo asigna una tarea a un departamento/especialista:

| Complejidad Tarea | Horas Meet |
|-------------------|------------|
| Simple (1 archivo, < 50 LOC) | 1 hora |
| Media (2-5 archivos, 50-200 LOC) | 1.5 horas |
| Compleja (> 5 archivos, > 200 LOC) | 2 horas |

### 3.2 Reuniones de Entrega

Cada entrega completada incluye tiempo de revision:

| Tipo Entrega | Horas Review |
|--------------|--------------|
| Parcial (feature incompleto) | 0.5 horas |
| Completa (feature listo) | 1 hora |
| Final (modulo completo) | 1.5 horas |

---

## 4. Formula de Calculo Total

### 4.1 Por Tarea Individual

```
Horas_Tarea = Horas_Meet + Horas_Desarrollo + Horas_Review

Donde:
  Horas_Desarrollo = ceil(LOC / Ratio_Nivel) * 2

  Ratio_Nivel:
    - Nivel 1: 50
    - Nivel 2: 30
    - Nivel 3: 20
```

### 4.2 Ejemplo Practico

**Tarea:** Implementar componente de animacion para dashboard
- Lineas estimadas: 85 LOC
- Nivel: 3 (Animation Expert, sub-especialista de UI)
- Complejidad: Media

```
Horas_Meet = 1.5h (complejidad media)
Horas_Desarrollo = ceil(85/20) * 2 = ceil(4.25) * 2 = 5 * 2 = 10h
Horas_Review = 1h (entrega completa)

TOTAL = 1.5 + 10 + 1 = 12.5 horas
```

---

## 5. Responsabilidades de Primo

### 5.1 Definicion de Equipo

Para cada proyecto, Primo debe:

1. **Analizar requerimientos** y determinar departamentos necesarios
2. **Identificar especialistas** requeridos por complejidad
3. **Asignar sub-especialistas** cuando la tarea lo requiera
4. **Documentar la estructura** del equipo en el proyecto

### 5.2 Estimacion Preliminar

Primo genera estimaciones basadas en:

```python
def estimar_proyecto(tareas: list) -> dict:
    """
    Genera estimacion preliminar de horas por departamento.
    """
    estimacion = {
        "total_horas": 0,
        "por_departamento": {},
        "por_nivel": {"nivel_1": 0, "nivel_2": 0, "nivel_3": 0},
        "reuniones": 0
    }

    for tarea in tareas:
        horas = calcular_horas_tarea(tarea)
        estimacion["total_horas"] += horas
        # ... distribuir por departamento y nivel

    return estimacion
```

### 5.3 Biblioteca de Recursos

Primo tiene acceso a la biblioteca de recursos disponibles:

```yaml
recursos_disponibles:
  nivel_1:
    - fronti_frontend
    - baky_backend
    - devi_devops
    - qai_testing
    - secu_security
    - mark_marketing

  nivel_2:
    frontend:
      - ux_designer
      - ui_designer
    backend:
      - api_architect
      - database_engineer
    # ...

  nivel_3:
    ux_designer:
      - seo_specialist
      - accessibility_expert
    ui_designer:
      - animation_expert
    # ...
```

---

## 6. Registro y Auditoria

### 6.1 Datos a Registrar por Tarea

```json
{
  "tarea_id": "TASK-001",
  "proyecto_id": "PROJ-001",
  "descripcion": "Implementar login con OAuth",
  "asignado_a": {
    "departamento": "baky_backend",
    "especialista": "api_architect",
    "sub_especialista": null
  },
  "nivel": 2,
  "metricas": {
    "loc_estimado": 120,
    "loc_real": 135,
    "horas_meet": 1.5,
    "horas_desarrollo_estimado": 8,
    "horas_desarrollo_real": 9.5,
    "horas_review": 1
  },
  "timestamps": {
    "asignada": "2026-01-30T10:00:00Z",
    "iniciada": "2026-01-30T11:30:00Z",
    "completada": "2026-01-30T21:00:00Z"
  }
}
```

### 6.2 Metricas de Proyecto

```json
{
  "proyecto_id": "PROJ-001",
  "resumen_horas": {
    "total": 156.5,
    "por_nivel": {
      "nivel_1": 80,
      "nivel_2": 56.5,
      "nivel_3": 20
    },
    "reuniones": 24,
    "desarrollo": 120,
    "review": 12.5
  },
  "precision_estimacion": 0.92
}
```

---

## 7. Actualizacion y Calibracion

Este sistema debe calibrarse periodicamente:

1. **Mensual:** Revisar precision de estimaciones vs realidad
2. **Trimestral:** Ajustar ratios si hay desviacion > 15%
3. **Anual:** Revision completa con nuevas fuentes de la industria

---

## Historial de Versiones

| Version | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2026-01-30 | Documento inicial |

---

*Documento generado por GriPro Project Management System*
*Basado en metodologias de estimacion de software reconocidas en la industria*
