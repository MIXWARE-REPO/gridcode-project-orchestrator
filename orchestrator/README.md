# Orchestrator (Primo)

## Descripción

Primo es el cerebro de GriPro. El Project Manager orchestrator que coordina todo el botequipo.

## Responsabilidades

- **Análisis de proyectos**: Lee y entiende especificaciones, contexto y repositorio completo
- **Planificación agile**: Genera backlog, define sprints, crea historias de usuario y tareas
- **Asignación inteligente**: Delega tareas a los agentes especializados según competencias
- **Coordinación**: Gestiona dependencias y secuencia de ejecución (paralelo/serial)
- **Control de calidad**: Revisa outputs de cada agente antes de continuar
- **Interfaz cliente**: Punto de contacto único con el usuario/cliente
- **Gestión de desviaciones**: Detecta y corrige problemas durante la ejecución

## Estructura

```
orchestrator/
├── pm_agent/          # Lógica del Project Manager
│   ├── __init__.py
│   ├── agent.py       # Clase principal del PM
│   ├── planner.py     # Generación de planes y backlog
│   └── coordinator.py # Coordinación de agentes
├── graph.py           # Definición del grafo LangGraph
├── state/             # Estado compartido
│   ├── __init__.py
│   ├── project_state.py
│   └── task_state.py
└── README.md          # Este archivo
```

## Tecnología

- **Framework**: LangGraph para orquestación de agentes
- **LLM**: Claude 3.5 Sonnet (Anthropic API)
- **Estado**: Memoria compartida entre agentes
- **Tools**: Git, file system, shell commands

## Estado

- [ ] Diseño de arquitectura
- [ ] Implementación del grafo base
- [ ] Módulo de planificación
- [ ] Módulo de coordinación
- [ ] Integración con agentes
- [ ] Testing
