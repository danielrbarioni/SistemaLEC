import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.solicitacao import Solicitacao

async def registrar_evento_historico(
    db: AsyncSession,
    tipo: str,
    origem_menu: str = "Usuários",
    evento_tipo: str = "EXECUCAO",
    detalhes: str = "",
    status: str = "CONCLUIDO",
    especialidade: str = "—",
    procedimento: str = "—",
    codigo_paciente: int = 0,
    nome_paciente: str = "—",
    perfil_executor: str = "",
    usuario: str = "",
    categorizacao: str = ""
) -> Solicitacao:
    """
    Registra um evento administrativo ou de auditoria na tabela de histórico/solicitações.
    """
    data_agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    novo_evento = Solicitacao(
        id=str(uuid.uuid4())[:8],
        tipo=tipo,
        especialidade=especialidade or "—",
        procedimento=procedimento or "—",
        codigo_paciente=codigo_paciente,
        nome_paciente=nome_paciente or "—",
        judicializado="Não",
        swallis="",
        medico_responsavel="",
        detalhes=detalhes or "—",
        tempo_standby=None,
        status=status,
        data_criacao=data_agora,
        perfil_executor=perfil_executor,
        usuario=usuario,
        procedimento_anterior="",
        origem_menu=origem_menu,
        evento_tipo=evento_tipo,
        categorizacao=categorizacao or None
    )
    db.add(novo_evento)
    return novo_evento
