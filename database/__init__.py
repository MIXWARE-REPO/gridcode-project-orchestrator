"""
Database Module
Persistencia de estado con Supabase PostgreSQL

Responsabilidades:
- Gestionar proyectos
- Persistir estado de agentes
- Registrar tareas completadas
- Mantener auditoría
- Gestionar conocimiento de Guru
"""

from .supabase_client import SupabaseManager

__version__ = "0.1.0"
__all__ = ["SupabaseManager"]
