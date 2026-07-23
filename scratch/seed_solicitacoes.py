import asyncio
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.models.solicitacao import Solicitacao

DB_URL = "sqlite+aiosqlite:///data/app.db"

async def seed_solicitacoes():
    engine = create_async_engine(DB_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        solic1 = Solicitacao(
            id=str(uuid.uuid4())[:8],
            tipo="INSERIR",
            especialidade="Plástica",
            procedimento="Mamoplastia",
            codigo_paciente=123456,
            nome_paciente="MARIA SILVA",
            judicializado="Não",
            swallis="A1",
            medico_responsavel="maria.carneiro",
            detalhes="Solicitação inicial de teste",
            status="PENDENTE",
            data_criacao=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            perfil_executor="ESPECIALIDADE",
            usuario="maria.carneiro",
            origem_menu="Pacientes",
            evento_tipo="SOLICITACAO"
        )
        session.add(solic1)
        await session.commit()
        print("Solicitação de teste adicionada com sucesso no app.db!")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_solicitacoes())
