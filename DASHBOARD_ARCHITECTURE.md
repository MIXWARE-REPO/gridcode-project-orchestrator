# 🎨 GriPro Dashboard - Arquitectura Completa

## Visión General

Dashboard interactivo y en tiempo real para clientes donde pueden:
- ✅ Ver estado actual de su proyecto
- - ✅ Revisar historial de intervenciones
  - - ✅ Chat directo con Primo (AI Project Manager)
    - - ✅ Recibir notificaciones en tiempo real
      - - ✅ Acceder por subdomain: `proyecto.evasoft.app`
       
        - ---

        ## 🏗️ Arquitectura General

        ```
        ┌────────────────────────────────────────────────────┐
        │   CLIENTE (Browser)                                │
        │  proyecto.evasoft.app                             │
        │  ┌──────────────────────────────────────────────┐ │
        │  │   Next.js Frontend + React Components        │ │
        │  │  - Dashboard Visual                          │ │
        │  │  - Project State Monitor                     │ │
        │  │  - Chat con Primo (WebSocket)                │ │
        │  │  - Activity Timeline                         │ │
        │  └──────────────────────────────────────────────┘ │
        └────────────────┬─────────────────────────────────┘
                         │ HTTPS + JWT Token
                         ▼
        ┌────────────────────────────────────────────────────┐
        │   API Gateway (Backend)                            │
        │  /api/projects/{id}                               │
        │  /api/projects/{id}/state                         │
        │  /api/projects/{id}/activities                    │
        │  /api/chat/primo                                  │
        │  /api/auth/validate-token                         │
        └────────────────┬─────────────────────────────────┘
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
          ┌──────┐   ┌──────┐   ┌────────┐
          │Primo │   │State │   │Supabase│
          │Agent │   │Mgr   │   │  DB    │
          └──────┘   └──────┘   └────────┘
             │           │           │
             └───────────┴───────────┘
                      ▼
             ┌────────────────────┐
             │  WebSocket Server  │
             │  (Tiempo Real)     │
             └────────────────────┘
        ```

        ---

        ## 📁 Estructura de Carpetas del Frontend

        ```
        frontend/
        ├── package.json                    # Dependencias
        ├── next.config.js                  # Config Next.js
        ├── tsconfig.json                   # TypeScript config
        ├── .env.example                    # Variables de entorno
        │
        ├── public/                         # Assets estáticos
        │   ├── logo.svg
        │   ├── favicon.ico
        │   └── images/
        │
        ├── src/
        │   ├── app/
        │   │   ├── layout.tsx              # Layout global
        │   │   ├── page.tsx                # Home page
        │   │   ├── dashboard/
        │   │   │   └── [projectId]/
        │   │   │       ├── page.tsx        # Dashboard principal
        │   │   │       ├── layout.tsx
        │   │   │       └── components/
        │   │   ├── auth/
        │   │   │   └── login/page.tsx      # Login page
        │   │   └── api/
        │   │       ├── projects/[id].ts
        │   │       ├── projects/[id]/state.ts
        │   │       ├── projects/[id]/activities.ts
        │   │       ├── chat/primo.ts
        │   │       └── auth/validate.ts
        │   │
        │   ├── components/
        │   │   ├── Dashboard/
        │   │   │   ├── ProjectHeader.tsx        # Encabezado del proyecto
        │   │   │   ├── StatusPanel.tsx          # Panel de estado
        │   │   │   ├── ActivityTimeline.tsx     # Historial de actividades
        │   │   │   ├── AgentCard.tsx            # Tarjeta de agente
        │   │   │   └── ProgressBar.tsx          # Barra de progreso
        │   │   │
        │   │   ├── Chat/
        │   │   │   ├── ChatBot.tsx              # Chat principal
        │   │   │   ├── MessageBubble.tsx        # Mensaje individual
        │   │   │   ├── InputField.tsx           # Campo de entrada
        │   │   │   └── ChatHistory.tsx          # Historial de chat
        │   │   │
        │   │   ├── Common/
        │   │   │   ├── Header.tsx               # Encabezado global
        │   │   │   ├── Sidebar.tsx              # Barra lateral
        │   │   │   ├── Footer.tsx               # Pie de página
        │   │   │   ├── Loader.tsx               # Indicador de carga
        │   │   │   └── NotificationBanner.tsx   # Banner de notificaciones
        │   │   │
        │   │   └── Auth/
        │   │       ├── LoginForm.tsx
        │   │       ├── ProtectedRoute.tsx
        │   │       └── VerifyToken.tsx
        │   │
        │   ├── hooks/
        │   │   ├── useProject.ts                # Hook para obtener proyecto
        │   │   ├── useChat.ts                   # Hook para chat
        │   │   ├── useWebSocket.ts              # Hook para WebSocket
        │   │   ├── useAuth.ts                   # Hook de autenticación
        │   │   └── useRealTimeUpdates.ts        # Hook para updates en tiempo real
        │   │
        │   ├── services/
        │   │   ├── api.ts                       # Cliente HTTP
        │   │   ├── websocket.ts                 # Cliente WebSocket
        │   │   ├── auth.ts                      # Servicios de autenticación
        │   │   └── projects.ts                  # Servicios de proyectos
        │   │
        │   ├── types/
        │   │   ├── project.ts                   # Tipos de datos
        │   │   ├── chat.ts
        │   │   ├── activity.ts
        │   │   └── auth.ts
        │   │
        │   ├── utils/
        │   │   ├── formatting.ts                # Utilidades de formato
        │   │   ├── date.ts                      # Utilidades de fecha
        │   │   ├── validators.ts                # Validadores
        │   │   └── constants.ts                 # Constantes
        │   │
        │   └── styles/
        │       ├── globals.css                  # Estilos globales
        │       ├── dashboard.module.css         # Módulos CSS
        │       └── tailwind.config.js           # Tailwind config
        │
        └── tests/
            ├── components/
            ├── hooks/
            ├── services/
            └── __mocks__/
        ```

        ---

        ## 🔐 Autenticación & Autorización

        ### Flujo de Login

        ```
        1. Cliente va a proyecto.evasoft.app
           ↓
        2. Sistema detecta que no tiene token
           ↓
        3. Redirige a /auth/login
           ↓
        4. Cliente ingresa:
           - Email del proyecto
           - Contraseña / código de acceso
           ↓
        5. Backend verifica en Supabase
           ↓
        6. Backend genera JWT token con:
           - project_id
           - client_email
           - exp (expiración)
           ↓
        7. Token se guarda en localStorage
           ↓
        8. Redirige a /dashboard/[projectId]
        ```

        ### Token JWT Structure

        ```json
        {
          "project_id": "uuid-of-project",
          "client_email": "cliente@example.com",
          "client_name": "Nombre Cliente",
          "access_level": "viewer|collaborator|admin",
          "exp": 1700000000,
          "iat": 1699000000,
          "iss": "gripro-dashboard"
        }
        ```

        ---

        ## 📊 Componentes Principales

        ### 1. ProjectHeader Component
        ```tsx
        // Muestra:
        - Nombre del proyecto
        - Estado general (En Progreso, Completado, En Pausa)
        - Porcentaje de avance general
        - Botón de exportar reporte
        ```

        ### 2. StatusPanel Component
        ```tsx
        // Muestra:
        - Estado actual del proyecto
        - Fase en la que se encuentra
        - Agentes activos / completados
        - Tiempo estimado de finalización
        - Indicadores de calidad
        ```

        ### 3. AgentCard Component
        ```tsx
        // Para cada agente (Primo, Fronti, Baky, etc):
        - Avatar/Icono del agente
        - Estado (Inactivo, Trabajando, Completado)
        - Tareas asignadas
        - Última actividad
        - Expandible para ver detalles
        ```

        ### 4. ActivityTimeline Component
        ```tsx
        // Muestra cronológicamente:
        - Inicio del proyecto
        - Cada intervención de agentes
        - Cambios de estado
        - Validaciones de Primo
        - Con timestamps y usuario responsable
        ```

        ### 5. ChatBot Component
        ```tsx
        // Chat en tiempo real con Primo:
        - Historial de conversación
        - Input field con envío
        - Typing indicators
        - Mensajes del sistema
        - Capacidad de adjuntar archivos (specs, etc)
        ```

        ---

        ## 🔌 API Endpoints Required

        Backend debe exponer estos endpoints:

        ```
        GET /api/projects/{projectId}
          Retorna: Datos del proyecto, estado, metadata
          Headers: Authorization: Bearer {token}

        GET /api/projects/{projectId}/state
          Retorna: Estado actual (% completo, fase, agentes activos)

        GET /api/projects/{projectId}/activities
          Retorna: Timeline de actividades (paginado)

        GET /api/projects/{projectId}/activities?limit=10&offset=0
          Paginación de actividades

        POST /api/chat/primo
          Body: { projectId, message }
          Retorna: { response, timestamp }

        WS /ws/projects/{projectId}
          WebSocket para actualizaciones en tiempo real
          Eventos:
            - state_update
            - agent_status_change
            - activity_new
            - chat_message

        POST /api/auth/validate-token
          Body: { token }
          Retorna: { valid, project_id, expiration }

        GET /api/auth/projects
          Retorna: Lista de proyectos del usuario autenticado
        ```

        ---

        ## 📡 WebSocket Events (Tiempo Real)

        El servidor debe emitir estos eventos:

        ```javascript
        // Estado del proyecto cambió
        ws.send(JSON.stringify({
          type: 'state_update',
          data: {
            projectId: 'xxx',
            progress: 45,
            phase: 'implementation',
            agentsActive: 3,
            timestamp: '2026-01-30T12:00:00Z'
          }
        }))

        // Un agente cambió de estado
        ws.send(JSON.stringify({
          type: 'agent_status_change',
          data: {
            agentId: 'fronti',
            status: 'working',
            currentTask: 'Optimizing SEO',
            progress: 60
          }
        }))

        // Nueva actividad
        ws.send(JSON.stringify({
          type: 'activity_new',
          data: {
            id: 'uuid',
            timestamp: '2026-01-30T12:00:00Z',
            agent: 'primo',
            action: 'validation_complete',
            description: 'Frontend validado exitosamente',
            icon: 'check'
          }
        }))

        // Nuevo mensaje del chat
        ws.send(JSON.stringify({
          type: 'chat_message',
          data: {
            from: 'primo',
            message: 'El frontend está listo para revisión',
            timestamp: '2026-01-30T12:00:00Z'
          }
        }))
        ```

        ---

        ## 🎨 Design System

        ### Color Palette
        ```
        Primary: #0066FF (Azul)
        Success: #00AA44 (Verde)
        Warning: #FF9900 (Naranja)
        Error: #FF3333 (Rojo)
        Dark: #1A1A1A
        Light: #F5F5F5
        ```

        ### Typography
        ```
        Font: Inter / Roboto
        H1: 32px, Bold
        H2: 24px, Bold
        H3: 18px, SemiBold
        Body: 14px, Regular
        Caption: 12px, Regular
        ```

        ### Components Base
        - Buttons, Inputs, Cards, Modal, Tooltip, Badge, Alert
        - - Responsive: Mobile, Tablet, Desktop
         
          - ---

          ## 🚀 Tecnologías Frontend

          ```json
          {
            "framework": "Next.js 14",
            "ui-library": "React 18",
            "styling": "Tailwind CSS",
            "realtime": "Socket.IO",
            "auth": "JWT + localStorage",
            "state": "React Context / Zustand",
            "http-client": "Axios / Fetch",
            "forms": "React Hook Form",
            "validation": "Zod",
            "testing": "Vitest / Testing Library"
          }
          ```

          ---

          ## 📱 Responsive Design

          ```
          Mobile (< 768px):
          - Single column layout
          - Hamburger menu
          - Bottom navigation
          - Full-width cards

          Tablet (768px - 1024px):
          - Two-column layout
          - Side panel navigation
          - Compact cards

          Desktop (> 1024px):
          - Three-column layout
          - Full sidebar
          - Detailed cards with hover effects
          ```

          ---

          ## 🔄 User Flow

          ### First-Time User
          ```
          1. Accede a proyecto.evasoft.app/proyecto-123
          2. No tiene token → Redirige a /auth/login
          3. Ingresa credenciales
          4. Sistema valida contra Supabase
          5. Genera JWT
          6. Redirige a /dashboard/proyecto-123
          7. Dashboard carga datos
          8. WebSocket se conecta
          ```

          ### Existing User
          ```
          1. Accede a proyecto.evasoft.app
          2. Token en localStorage
          3. Valida token con backend
          4. Carga dashboard automáticamente
          5. WebSocket recibe updates en tiempo real
          6. Chat conecta a Primo
          ```

          ---

          ## 📈 Performance Optimization

          - Server-Side Rendering (SSR) en Next.js
          - - Static Generation (SSG) para páginas públicas
            - - Image Optimization con Next.js Image
              - - Code Splitting automático
                - - Lazy loading de componentes
                  - - Caching de requests HTTP
                    - - WebSocket reconnection automático
                     
                      - ---

                      ## 🔒 Security Considerations

                      - JWT tokens en httpOnly cookies (si es posible)
                      - - HTTPS required
                        - - CORS properly configured
                          - - XSS protection con Content Security Policy
                            - - CSRF tokens si es necesario
                              - - Rate limiting en API
                                - - Input validation en frontend y backend
                                 
                                  - ---

                                  ## ✨ Next Steps for Frontend Implementation

                                  1. Create Next.js project structure
                                  2. 2. Setup Tailwind CSS
                                     3. 3. Create authentication pages
                                        4. 4. Create dashboard components
                                           5. 5. Setup API integration
                                              6. 6. Setup WebSocket connection
                                                 7. 7. Create hooks for data fetching
                                                    8. 8. Implement real-time updates
                                                       9. 9. Add form validation
                                                          10. 10. Create comprehensive tests
                                                             
                                                              11. ---
                                                             
                                                              12. **Esta arquitectura permite que cada cliente tenga su dashboard seguro y personalizado!**
