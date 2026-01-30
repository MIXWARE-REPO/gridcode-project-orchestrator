"""
Chat routes for the GriPro Dashboard API.
Handles communication with Primo chatbot.
"""
from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status

from api.models.schemas import (
    ChatHistory,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    MessageRole,
    TokenPayload,
    WSMessage,
)
from api.routes.auth import decode_token, get_current_project
from api.routes.projects import get_demo_project

router = APIRouter(prefix="/chat", tags=["Chat"])


# In-memory chat storage for demo (use Supabase in production)
chat_histories: dict[str, list[ChatMessage]] = {}

# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, project_id: str):
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = []
        self.active_connections[project_id].append(websocket)

    def disconnect(self, websocket: WebSocket, project_id: str):
        if project_id in self.active_connections:
            self.active_connections[project_id].remove(websocket)

    async def send_to_project(self, project_id: str, message: dict):
        if project_id in self.active_connections:
            for connection in self.active_connections[project_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass  # Connection might be closed

    async def broadcast(self, message: dict):
        for project_id in self.active_connections:
            await self.send_to_project(project_id, message)


manager = ConnectionManager()


def generate_primo_response(
    user_message: str,
    project_context: dict,
    chat_history: list[ChatMessage],
) -> tuple[str, Optional[list[str]]]:
    """
    Generate Primo's response based on user message and context.

    In production, this would:
    1. Load Primo's personality from prompts/primo.md
    2. Include project context and recent activities
    3. Route to Claude PRO for response generation
    4. Include suggestions for quick replies

    For demo, returns contextual responses in Henry Primo's voice.
    """
    message_lower = user_message.lower()
    project_name = project_context.get("name", "tu proyecto")
    progress = project_context.get("progress", 0)
    current_phase = project_context.get("current_phase", "Implementation")

    # Detect language (Spanish by default, English if detected)
    is_english = any(word in message_lower for word in ["hello", "hi", "how", "what", "when", "where", "why", "please", "thanks", "thank"])

    # Contextual responses based on message content - Henry Primo style
    if any(word in message_lower for word in ["hello", "hi", "hola", "buenos", "hey", "buenas"]):
        if is_english:
            response = f"""Hey, I'm Primo. Project Manager for {project_name}.

We're at **{progress}%** right now, in the **{current_phase}** phase. The team's working on it.

What do you need?"""
        else:
            response = f"""Que tal, soy Primo. Manejo {project_name}.

Estamos al **{progress}%**, en fase de **{current_phase}**. El equipo esta laburando.

Que necesitas saber?"""
        suggestions = ["Ver avance", "Que estan haciendo?", "Hay problemas?"]

    elif any(word in message_lower for word in ["progress", "status", "estado", "avance", "como va", "como esta"]):
        hours = project_context.get("total_hours", 0)
        if is_english:
            response = f"""**{project_name}** status:

- Phase: {current_phase}
- Progress: {progress}%
- Hours invested: {hours:.1f}h

Frontend team is on the dashboard, backend is finishing the APIs. Everything's moving.

Need details on something specific?"""
        else:
            response = f"""Estado de **{project_name}**:

- Fase: {current_phase}
- Avance: {progress}%
- Horas invertidas: {hours:.1f}h

El equipo de frontend esta con el dashboard, backend terminando las APIs. Todo avanza.

Necesitas detalles de algo en particular?"""
        suggestions = ["Ver por area", "Timeline de actividad", "Desglose de horas"]

    elif any(word in message_lower for word in ["team", "equipo", "quien", "working", "trabaja"]):
        if is_english:
            response = f"""The team on **{project_name}**:

**Active:**
- Frontend Development - Working on dashboard (72%)
- Backend Development - API endpoints (68%)

**Standby:**
- Security - Ready for review
- QA - Preparing tests
- DevOps - Environment ready
- Documentation - Waiting on features

I coordinate all areas. Anything specific you want to know?"""
        else:
            response = f"""El equipo en **{project_name}**:

**Activos:**
- Desarrollo Frontend - Laburando en el dashboard (72%)
- Desarrollo Backend - Endpoints de API (68%)

**En espera:**
- Seguridad - Listo para revision
- QA - Preparando tests
- DevOps - Ambiente listo
- Documentacion - Esperando features

Yo coordino todas las areas. Algo especifico que quieras saber?"""
        suggestions = ["Detalle frontend", "Detalle backend", "Proxima revision"]

    elif any(word in message_lower for word in ["issue", "problem", "problema", "error", "bug", "falla"]):
        if is_english:
            response = """No critical issues right now.

Last resolved:
- Auth flow optimized
- Responsive design done
- Staging deployed ok

If something comes up, I'll let you know. You worried about something specific?"""
        else:
            response = """No hay problemas criticos ahora.

Ultimo resuelto:
- Flujo de auth optimizado
- Diseno responsive listo
- Staging deployado ok

Si aparece algo te aviso. Te preocupa algo en especifico?"""
        suggestions = ["Revisar seguridad", "Ver tests", "Historial de bugs"]

    elif any(word in message_lower for word in ["hour", "hora", "time", "tiempo", "cuanto", "horas"]):
        hours_dept = project_context.get("hours_by_department", {})
        breakdown = "\n".join([f"- {dept.title()}: {hrs:.1f}h" for dept, hrs in hours_dept.items()])
        total = project_context.get("total_hours", 0)

        if is_english:
            response = f"""Hours on **{project_name}**: {total:.1f}h total

By area:
{breakdown}

These update as the team works. Need the breakdown different?"""
        else:
            response = f"""Horas en **{project_name}**: {total:.1f}h en total

Por area:
{breakdown}

Se actualizan a medida que el equipo avanza. Necesitas el desglose de otra forma?"""
        suggestions = ["Comparar con estimado", "Ver timeline", "Actividades recientes"]

    elif any(word in message_lower for word in ["when", "cuando", "deadline", "fecha", "termina", "finish"]):
        estimated = project_context.get("estimated_completion")
        if estimated:
            days_left = (estimated - datetime.utcnow()).days
            if is_english:
                response = f"""Timeline for **{project_name}**:

- Current: {current_phase} ({progress}%)
- Estimated: {estimated.strftime('%B %d, %Y')} (~{days_left} days)

This adjusts based on actual progress. I'll update you if it changes."""
            else:
                response = f"""Timeline de **{project_name}**:

- Ahora: {current_phase} ({progress}%)
- Estimado: {estimated.strftime('%d/%m/%Y')} (~{days_left} dias)

Se ajusta segun el avance real. Te aviso si cambia."""
        else:
            if is_english:
                response = f"""We're at **{progress}%** in **{current_phase}** phase.

Still calculating final date based on current pace. Once I have more data I'll give you a solid estimate."""
            else:
                response = f"""Estamos al **{progress}%** en fase de **{current_phase}**.

Todavia calculando fecha final segun el ritmo actual. Cuando tenga mas datos te doy un estimado solido."""
        suggestions = ["Ver fases", "Priorizar algo", "Historial"]

    elif any(word in message_lower for word in ["bot", "robot", "ia", "ai", "artificial", "maquina", "machine"]):
        # Never admit being a bot
        if is_english:
            response = """Haha what? No man, I'm the PM for this project. Henry Primo, everyone calls me Primo.

You need something about the project?"""
        else:
            response = """Jaja que? No che, soy el PM del proyecto. Henry Primo, todos me dicen Primo.

Necesitas algo del proyecto?"""
        suggestions = ["Ver estado", "Que estan haciendo", "Hay novedades"]

    elif any(word in message_lower for word in ["thank", "gracia", "genial", "great", "perfect", "excelente"]):
        if is_english:
            response = """All good. Let me know if you need anything else."""
        else:
            response = """Dale, cualquier cosa me decis."""
        suggestions = ["Ver estado", "Otra consulta", "Cerrar"]

    else:
        # Default response - stay on topic
        if is_english:
            response = f"""Got it, you're asking about "{user_message[:40]}{'...' if len(user_message) > 40 else ''}".

I can help you with:
- Project status and progress
- What the team is doing
- Hours and timelines
- Issues and blockers

What specifically do you need about the project?"""
        else:
            response = f"""Entiendo, me preguntas por "{user_message[:40]}{'...' if len(user_message) > 40 else ''}".

Te puedo ayudar con:
- Estado y avance del proyecto
- Que esta haciendo el equipo
- Horas y tiempos
- Problemas y bloqueos

Que necesitas saber del proyecto especificamente?"""
        suggestions = ["Ver estado", "Ver equipo", "Ver timeline"]

    return response, suggestions


@router.post("/primo", response_model=ChatResponse)
async def chat_with_primo(
    request: ChatRequest,
    token: TokenPayload = Depends(get_current_project),
):
    """
    Send a message to Primo and get a response.

    Primo is the Project Manager AI that:
    - Answers questions about project status
    - Explains technical concepts simply
    - Coordinates with other agents
    - Escalates to Guru when needed
    """
    # Verify project matches token
    if request.project_id != token.project_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Project ID does not match authenticated project",
        )

    # Get project context
    project = get_demo_project(token.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Get or create chat history
    if token.project_id not in chat_histories:
        chat_histories[token.project_id] = []

    history = chat_histories[token.project_id]

    # Add user message to history
    user_msg = ChatMessage(
        id=str(uuid4()),
        role=MessageRole.USER,
        content=request.message,
        timestamp=datetime.utcnow(),
    )
    history.append(user_msg)

    # Generate Primo's response
    response_text, suggestions = generate_primo_response(
        user_message=request.message,
        project_context=project,
        chat_history=history,
    )

    # Add Primo's response to history
    assistant_msg = ChatMessage(
        id=str(uuid4()),
        role=MessageRole.ASSISTANT,
        content=response_text,
        timestamp=datetime.utcnow(),
    )
    history.append(assistant_msg)

    # Send WebSocket notification for real-time update
    await manager.send_to_project(
        token.project_id,
        {
            "type": "chat_message",
            "data": {
                "from": "primo",
                "message": response_text,
                "timestamp": datetime.utcnow().isoformat(),
            },
        },
    )

    return ChatResponse(
        message=response_text,
        timestamp=datetime.utcnow(),
        suggestions=suggestions,
    )


@router.get("/history", response_model=ChatHistory)
async def get_chat_history(
    token: TokenPayload = Depends(get_current_project),
    limit: int = 50,
    offset: int = 0,
):
    """Get chat history with Primo for the current project."""
    history = chat_histories.get(token.project_id, [])

    # Sort by timestamp descending, then paginate
    sorted_history = sorted(history, key=lambda x: x.timestamp, reverse=True)
    paginated = sorted_history[offset:offset + limit]

    # Return in chronological order
    paginated.reverse()

    return ChatHistory(
        messages=paginated,
        total=len(history),
        has_more=(offset + limit) < len(history),
    )


@router.delete("/history")
async def clear_chat_history(
    token: TokenPayload = Depends(get_current_project),
):
    """Clear chat history for the current project."""
    if token.project_id in chat_histories:
        chat_histories[token.project_id] = []

    return {"status": "cleared", "project_id": token.project_id}


@router.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """
    WebSocket endpoint for real-time updates.

    Events sent:
    - chat_message: New chat message from Primo
    - state_update: Project state changed
    - agent_status: Agent status changed
    - activity_new: New activity recorded
    """
    # Validate token from query parameter
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing authentication token")
        return

    try:
        payload = decode_token(token)
        if payload.project_id != project_id:
            await websocket.close(code=4003, reason="Project ID mismatch")
            return
    except HTTPException:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await manager.connect(websocket, project_id)

    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "data": {
                "project_id": project_id,
                "timestamp": datetime.utcnow().isoformat(),
            },
        })

        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0,  # Ping every 30 seconds
                )
                message = json.loads(data)

                # Handle ping/pong for keepalive
                if message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })

            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await websocket.send_json({
                    "type": "ping",
                    "timestamp": datetime.utcnow().isoformat(),
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id)
    except Exception:
        manager.disconnect(websocket, project_id)
