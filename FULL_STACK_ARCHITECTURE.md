# 🏢 GriPro - Arquitectura Full-Stack Completa

## 📋 Índice de Documentación

Lee estos documentos en orden:
1. **Este archivo** - Visión general (donde estás)
2. 2. `IMPLEMENTATION_GUIDE.md` - Guía de implementación backend
   3. 3. `DASHBOARD_ARCHITECTURE.md` - Arquitectura frontend/UX
     
      4. ---
     
      5. ## 🎯 Visión 360 del Sistema
     
      6. GriPro es un sistema **enterprise-ready** que automatiza desarrollo de software con IA, combinando:
     
      7. - **Backend Inteligente** (Python + LangGraph) - Orquestación de agentes
         - - **Frontend Interactivo** (Next.js + React) - Dashboard para clientes
           - - **Base de Datos** (Supabase/PostgreSQL) - Persistencia
             - - **Comunicación Tiempo Real** (WebSocket) - Updates en vivo
               - - **Autenticación Segura** (JWT) - Por proyecto/cliente
                
                 - ---

                 ## 🏗️ Arquitectura Global

                 ```
                                           INTERNET
                                              │
                         ┌────────────────────┼────────────────────┐
                         │                    │                    │
                         ▼                    ▼                    ▼
                    ┌─────────────┐    ┌────────────────┐   ┌──────────────┐
                    │  CLIENTE 1  │    │  CLIENTE N     │   │  INTERNO     │
                    │ proyecto.  │    │ otro-proyecto. │   │  (admin)     │
                    │ evasoft.   │    │ evasoft.app    │   │  evasoft.    │
                    │ app        │    │                │   │  app/admin   │
                    └─────────────┘    └────────────────┘   └──────────────┘
                         │                    │                    │
                         └────────────────────┼────────────────────┘
                                              │
                                         HTTPS + JWT
                                              │
                         ┌────────────────────▼────────────────────┐
                         │     API Gateway (Backend Python)        │
                         │  /api/projects/{id}                    │
                         │  /api/chat/primo                       │
                         │  /api/auth/validate                    │
                         │  /ws/projects/{id}                     │
                         └────────────────────┬────────────────────┘
                                              │
                         ┌────────────────────┼────────────────────┐
                         ▼                    ▼                    ▼
                    ┌──────────┐        ┌───────────┐      ┌──────────────┐
                    │ LangGraph│        │ LLM Router│      │  Supabase    │
                    │ Orquestador      │(Claude,   │      │  PostgreSQL  │
                    │(Primo +  │        │Gemini)    │      │              │
                    │ Agentes) │        └───────────┘      └──────────────┘
                    └──────────┘
                         │
                         └─────────────┬─────────────┐
                                       ▼
                               ┌───────────────────┐
                               │  WebSocket Server │
                               │  (Tiempo Real)    │
                               └───────────────────┘
                                       ▲
                                       │
                               ┌───────┴──────────┐
                               │  Socket.IO       │
                               │  Events:         │
                               │  - state_update  │
                               │  - agent_status  │
                               │  - activities    │
                               │  - chat_msg      │
                               └──────────────────┘
                 ```

                 ---

                 ## 📦 Componentes Principales

                 ### 1. Backend (Python)

                 **Ubicación:** Raíz del repositorio

                 **Responsabilidades:**
                 - Orquestación de agentes con LangGraph
                 - - Manejo de proyectos y estado
                   - - Autenticación JWT
                     - - APIs REST para frontend
                       - - WebSocket para tiempo real
                         - - Integración con Supabase
                          
                           - **Carpetas Clave:**
                           - - `/core` - Orquestador y routers
                             - - `/auth` - Gestión de credenciales
                               - - `/database` - Cliente Supabase
                                 - - `/agents` - Agentes especializados
                                   - - `/config` - Configuración centralizada
                                    
                                     - **Tecnologías:**
                                     - - Python 3.11+
                                       - - LangGraph 0.0.41
                                         - - FastAPI (para APIs)
                                           - - Socket.IO (para WebSocket)
                                             - - Supabase SDK
                                              
                                               - ### 2. Frontend (Next.js)
                                              
                                               - **Ubicación:** `/frontend` (a crear)
                                              
                                               - **Responsabilidades:**
                                               - - Dashboard visual para clientes
                                                 - - Chat con Primo
                                                   - - Autenticación por JWT
                                                     - - Updates en tiempo real vía WebSocket
                                                       - - Responsive design
                                                        
                                                         - **Carpetas Clave:**
                                                         - - `/src/app` - Pages y layouts
                                                           - - `/src/components` - Componentes React
                                                             - - `/src/hooks` - Hooks personalizados
                                                               - - `/src/services` - Servicios API
                                                                 - - `/src/types` - Tipos TypeScript
                                                                  
                                                                   - **Tecnologías:**
                                                                   - - Next.js 14
                                                                     - - React 18
                                                                       - - TypeScript
                                                                         - - Tailwind CSS
                                                                           - - Socket.IO Client
                                                                             - - Zustand o React Context
                                                                              
                                                                               - ### 3. Base de Datos (Supabase/PostgreSQL)
                                                                              
                                                                               - **Ubicación:** Cloud (Supabase)
                                                                              
                                                                               - **Tablas Principales:**
                                                                               - - `projects` - Metadatos de proyectos
                                                                                 - - `agent_state` - Estado de cada agente
                                                                                   - - `tasks` - Tareas generadas
                                                                                     - - `activities` - Historial de actividades
                                                                                       - - `chat_messages` - Mensajes del chat
                                                                                         - - `users` - Usuarios/clientes
                                                                                           - - `audit_logs` - Auditoría de operaciones
                                                                                            
                                                                                             - ---

                                                                                             ## 🔄 Flujo Completo de Uso

                                                                                             ### Escenario: Cliente Accede a su Dashboard

                                                                                             ```
                                                                                             1. CLIENTE ACCEDE
                                                                                                └─> Va a proyecto.evasoft.app/proyecto-123

                                                                                             2. AUTENTICACIÓN
                                                                                                └─> No tiene JWT token
                                                                                                └─> Redirige a /auth/login
                                                                                                └─> Ingresa email + password
                                                                                                └─> Backend valida contra Supabase
                                                                                                └─> Genera JWT con project_id
                                                                                                └─> Token se guarda en localStorage

                                                                                             3. DASHBOARD CARGA
                                                                                                └─> Hace request: GET /api/projects/proyecto-123
                                                                                                └─> Backend obtiene datos de Supabase
                                                                                                └─> Frontend renderiza componentes

                                                                                             4. WebSocket SE CONECTA
                                                                                                └─> Cliente abre conexión: WS /ws/projects/proyecto-123
                                                                                                └─> Servidor autoriza con JWT
                                                                                                └─> Cliente listo para recibir eventos

                                                                                             5. ACTUALIZACIÓN EN TIEMPO REAL
                                                                                                └─> Primo completa una validación
                                                                                                └─> Backend emite: { type: 'activity_new', ... }
                                                                                                └─> Cliente recibe en tiempo real
                                                                                                └─> UI se actualiza automáticamente

                                                                                             6. CLIENTE CHATEA CON PRIMO
                                                                                                └─> Cliente escribe en ChatBot
                                                                                                └─> POST /api/chat/primo
                                                                                                └─> Backend pasa mensaje a Primo agent
                                                                                                └─> Primo genera respuesta
                                                                                                └─> Mensaje vuelve al cliente en tiempo real
                                                                                                └─> Chat se actualiza
                                                                                             ```

                                                                                             ---

                                                                                             ## 🔐 Seguridad & Autenticación

                                                                                             ### Flujo de Token JWT

                                                                                             ```json
                                                                                             TOKEN EN HEADER:
                                                                                             Authorization: Bearer eyJhbGc...

                                                                                             PAYLOAD:
                                                                                             {
                                                                                               "project_id": "proj-123",
                                                                                               "client_email": "cliente@empresa.com",
                                                                                               "client_name": "Empresa X",
                                                                                               "access_level": "viewer",
                                                                                               "exp": 1735689600,
                                                                                               "iat": 1700000000
                                                                                             }

                                                                                             VALIDACIÓN:
                                                                                             1. Frontend obtiene token en login
                                                                                             2. Frontend envía en header Authorization
                                                                                             3. Backend valida firma JWT
                                                                                             4. Backend verifica project_id coincida
                                                                                             5. Backend verifica expiration
                                                                                             6. Si válido → permite operación
                                                                                             7. Si inválido → retorna 401 Unauthorized
                                                                                             ```

                                                                                             ### Niveles de Acceso

                                                                                             ```
                                                                                             viewer:       Solo lectura del dashboard
                                                                                             collaborator: Puede chatear con Primo
                                                                                             admin:        Control total (futuro)
                                                                                             ```

                                                                                             ---

                                                                                             ## 📡 Comunicación en Tiempo Real

                                                                                             ### WebSocket Events

                                                                                             El servidor **emite** estos eventos a los clientes:

                                                                                             ```javascript
                                                                                             // Cada 5 minutos o cuando cambia
                                                                                             {
                                                                                               type: 'state_update',
                                                                                               data: {
                                                                                                 progress: 45,           // %
                                                                                                 phase: 'implementation',
                                                                                                 agentsActive: 3,
                                                                                                 estimatedCompletion: '2026-02-15'
                                                                                               }
                                                                                             }

                                                                                             // Cuando un agente cambia de tarea
                                                                                             {
                                                                                               type: 'agent_status_change',
                                                                                               data: {
                                                                                                 agentId: 'fronti',
                                                                                                 status: 'working',
                                                                                                 task: 'Optimizing SEO metadata',
                                                                                                 progress: 75
                                                                                               }
                                                                                             }

                                                                                             // Nueva actividad completada
                                                                                             {
                                                                                               type: 'activity_new',
                                                                                               data: {
                                                                                                 id: 'act-123',
                                                                                                 timestamp: '2026-01-30T14:30:00Z',
                                                                                                 agent: 'primo',
                                                                                                 action: 'validation_complete',
                                                                                                 description: 'Frontend validado ✓',
                                                                                                 icon: 'check'
                                                                                               }
                                                                                             }

                                                                                             // Nuevo mensaje en chat
                                                                                             {
                                                                                               type: 'chat_message',
                                                                                               data: {
                                                                                                 id: 'msg-456',
                                                                                                 from: 'primo',
                                                                                                 message: 'El frontend está listo para producción',
                                                                                                 timestamp: '2026-01-30T14:35:00Z'
                                                                                               }
                                                                                             }
                                                                                             ```

                                                                                             ---

                                                                                             ## 🚀 Deployment

                                                                                             ### Estructura de Deployments

                                                                                             ```
                                                                                             ┌──────────────────────────────────────┐
                                                                                             │  Frontend: Vercel                    │
                                                                                             │  proyecto.evasoft.app               │
                                                                                             │  (Next.js automáticamente)           │
                                                                                             └──────────────────────────────────────┘

                                                                                             ┌──────────────────────────────────────┐
                                                                                             │  Backend: Hetzner VPS                │
                                                                                             │  api.evasoft.app                     │
                                                                                             │  (Docker container)                  │
                                                                                             └──────────────────────────────────────┘

                                                                                             ┌──────────────────────────────────────┐
                                                                                             │  Database: Supabase (PostgreSQL)     │
                                                                                             │  Cloud-hosted                        │
                                                                                             └──────────────────────────────────────┘

                                                                                             ┌──────────────────────────────────────┐
                                                                                             │  DNS/Routing: Dreamhost              │
                                                                                             │  *.evasoft.app → API                 │
                                                                                             │  proyecto.evasoft.app → Frontend     │
                                                                                             └──────────────────────────────────────┘
                                                                                             ```

                                                                                             ---

                                                                                             ## 📊 Stack Tecnológico Completo

                                                                                             ### Backend
                                                                                             - **Language:** Python 3.11+
                                                                                             - - **Framework:** FastAPI / Flask
                                                                                               - - **Orchestration:** LangGraph 0.0.41
                                                                                                 - - **LLM:** Anthropic Claude + Google Gemini
                                                                                                   - - **Database:** Supabase/PostgreSQL
                                                                                                     - - **WebSocket:** Socket.IO
                                                                                                       - - **Auth:** JWT
                                                                                                         - - **Async:** asyncio, aiohttp
                                                                                                           - - **Deployment:** Docker en Hetzner
                                                                                                            
                                                                                                             - ### Frontend
                                                                                                             - - **Framework:** Next.js 14
                                                                                                               - - **UI:** React 18
                                                                                                                 - - **Language:** TypeScript
                                                                                                                   - - **Styling:** Tailwind CSS
                                                                                                                     - - **State:** React Context / Zustand
                                                                                                                       - - **Real-time:** Socket.IO Client
                                                                                                                         - - **HTTP:** Axios / Fetch API
                                                                                                                           - - **Forms:** React Hook Form
                                                                                                                             - - **Validation:** Zod
                                                                                                                               - - **Deployment:** Vercel
                                                                                                                                
                                                                                                                                 - ### Infrastructure
                                                                                                                                 - - **VPS:** Hetzner (backend + DB tunneling)
                                                                                                                                   - - **CDN:** Vercel Edge Network (frontend)
                                                                                                                                     - - **Database:** Supabase (managed PostgreSQL)
                                                                                                                                       - - **DNS:** Dreamhost
                                                                                                                                         - - **CI/CD:** GitHub Actions
                                                                                                                                           - - **Monitoring:** Supabase monitoring + Hetzner metrics
                                                                                                                                            
                                                                                                                                             - ---
                                                                                                                                             
                                                                                                                                             ## 📈 Flujo de Desarrollo
                                                                                                                                             
                                                                                                                                             ### Orden Recomendado de Implementación
                                                                                                                                             
                                                                                                                                             **Fase 1: Backend Base** (Semanas 1-2)
                                                                                                                                             1. ✅ Estructura inicial (ya hecha)
                                                                                                                                             2. 2. → auth/credentials_manager.py
                                                                                                                                                3. 3. → config/settings.py
                                                                                                                                                   4. 4. → core/llm_router.py
                                                                                                                                                      5. 5. → core/agent_registry.py
                                                                                                                                                         6. 6. → database/supabase_client.py
                                                                                                                                                            7. 7. → core/gripro_orchestrator.py
                                                                                                                                                              
                                                                                                                                                               8. **Fase 2: APIs** (Semana 3)
                                                                                                                                                               9. 1. → Crear FastAPI app
                                                                                                                                                                  2. 2. → Implementar endpoints /api/projects
                                                                                                                                                                     3. 3. → Implementar /api/chat/primo
                                                                                                                                                                        4. 4. → Implementar /api/auth
                                                                                                                                                                           5. 5. → Setup WebSocket /ws
                                                                                                                                                                             
                                                                                                                                                                              6. **Fase 3: Frontend** (Semanas 4-5)
                                                                                                                                                                              7. 1. → Crear proyecto Next.js
                                                                                                                                                                                 2. 2. → Setup Tailwind CSS
                                                                                                                                                                                    3. 3. → Crear pages/auth/login
                                                                                                                                                                                       4. 4. → Crear pages/dashboard/[projectId]
                                                                                                                                                                                          5. 5. → Crear componentes Dashboard
                                                                                                                                                                                             6. 6. → Crear componentes Chat
                                                                                                                                                                                                7. 7. → Setup Socket.IO client
                                                                                                                                                                                                   8. 8. → Integración con APIs
                                                                                                                                                                                                     
                                                                                                                                                                                                      9. **Fase 4: Integration & Testing** (Semana 6)
                                                                                                                                                                                                      10. 1. → End-to-end testing
                                                                                                                                                                                                          2. 2. → Security audit
                                                                                                                                                                                                             3. 3. → Performance optimization
                                                                                                                                                                                                                4. 4. → Documentation
                                                                                                                                                                                                                  
                                                                                                                                                                                                                   5. **Fase 5: Deployment** (Semana 7)
                                                                                                                                                                                                                   6. 1. → Deploy backend a Hetzner
                                                                                                                                                                                                                      2. 2. → Deploy frontend a Vercel
                                                                                                                                                                                                                         3. 3. → Setup DNS subdominios
                                                                                                                                                                                                                            4. 4. → Configurar SSL/HTTPS
                                                                                                                                                                                                                               5. 5. → Monitoreo en producción
                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                  6. ---
                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                  7. ## 💡 Key Features Summary
                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                  8. ✅ **Orquestación Inteligente** - LangGraph coordina agentes
                                                                                                                                                                                                                                  9. ✅ **Multi-Agentes** - 8+ agentes especializados
                                                                                                                                                                                                                                  10. ✅ **Dashboard Cliente** - Visual e interactivo
                                                                                                                                                                                                                                  11. ✅ **Chat con IA** - Primo responde preguntas en tiempo real
                                                                                                                                                                                                                                  12. ✅ **Tiempo Real** - WebSocket para actualizaciones instantáneas
                                                                                                                                                                                                                                  13. ✅ **Autenticación Segura** - JWT por proyecto
                                                                                                                                                                                                                                  14. ✅ **Persistencia** - Supabase para todo
                                                                                                                                                                                                                                  15. ✅ **Escalable** - Fácil agregar nuevos clientes/proyectos
                                                                                                                                                                                                                                  16. ✅ **Enterprise** - Listo para producción
                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                  17. ---
                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                  18. ## 📚 Documentación de Referencia
                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                  19. Documentos clave en el repositorio:
                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                  20. 1. `IMPLEMENTATION_GUIDE.md` - Cómo implementar backend
                                                                                                                                                                                                                                      2. 2. `DASHBOARD_ARCHITECTURE.md` - Cómo implementar frontend
                                                                                                                                                                                                                                         3. 3. `SETUP.md` - Setup inicial rápido
                                                                                                                                                                                                                                            4. 4. `docs/architecture.md` - Jerarquía de agentes
                                                                                                                                                                                                                                               5. 5. `docs/agents-complete.md` - Descripción de cada agente
                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                  6. ---
                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                  7. ## ✨ Visión Final
                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                  8. Este sistema permite:
                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                  9. 🎯 **Para la Empresa:**
                                                                                                                                                                                                                                                  10. - Automatizar desarrollo 100%
                                                                                                                                                                                                                                                      - - Reducir costos operacionales
                                                                                                                                                                                                                                                        - - Mantener clientes informados en tiempo real
                                                                                                                                                                                                                                                          - - Escalar a múltiples proyectos simultáneos
                                                                                                                                                                                                                                                           
                                                                                                                                                                                                                                                            - 🎯 **Para los Clientes:**
                                                                                                                                                                                                                                                            - - Ver progreso de su proyecto en vivo
                                                                                                                                                                                                                                                              - - Chatear directamente con IA (Primo)
                                                                                                                                                                                                                                                                - - Acceso seguro por subdomain
                                                                                                                                                                                                                                                                  - - Transparencia total
                                                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                                    - 🎯 **Para los Desarrolladores:**
                                                                                                                                                                                                                                                                    - - Código bien estructurado y documentado
                                                                                                                                                                                                                                                                      - - Componentes reutilizables
                                                                                                                                                                                                                                                                        - - Easy to extend y mantener
                                                                                                                                                                                                                                                                          - - Testing integrado
                                                                                                                                                                                                                                                                           
                                                                                                                                                                                                                                                                            - ---
                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                            **¡Tu sistema GriPro está completamente diseñado y documentado!**
                                                                                                                                                                                                                                                                            **Ahora solo falta la implementación en VSCode.**
