# src/resources/database.py

import os
from typing import AsyncGenerator
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Base para os modelos do banco de dados da aplicação (SQLite)
Base = declarative_base()

class DatabaseManager:
    """
    Manages asynchronous database connections and sessions for a specific DSN.
    """
    def __init__(self, dsn: str):
        self.engine: AsyncEngine = create_async_engine(dsn, echo=False)
        self.async_session_maker = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Provides an asynchronous session for database operations.
        """
        async with self.async_session_maker() as session:
            try:
                yield session
            finally:
                await session.close()

    async def close_connection(self):
        """
        Closes all connections in the engine's connection pool.
        """
        await self.engine.dispose()

_default_app_db_manager = None

def get_default_app_db_manager() -> DatabaseManager:
    global _default_app_db_manager
    if _default_app_db_manager is None:
        dsn = os.getenv("SQLITE_DSN", "sqlite+aiosqlite:///./data/app.db")
        _default_app_db_manager = DatabaseManager(dsn)
    return _default_app_db_manager

async def get_aghu_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI to get an AGHU database session from the app state.
    """
    if hasattr(request.app.state, "aghu_db") and request.app.state.aghu_db:
        async for session in request.app.state.aghu_db.get_session():
            yield session
    else:
        # Se não houver banco AGHU configurado, gera sessão vazia/None
        return

async def get_app_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI to get an application database session (SQLite) from the app state, com fallback automático.
    """
    if hasattr(request.app.state, "app_db") and request.app.state.app_db:
        manager = request.app.state.app_db
    else:
        manager = get_default_app_db_manager()
    
    async for session in manager.get_session():
        yield session
