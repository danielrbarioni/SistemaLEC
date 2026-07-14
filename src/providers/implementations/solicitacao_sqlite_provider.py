import uuid
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException, status

from ..interfaces.solicitacao_provider_interface import SolicitacaoProviderInterface
from ...models.solicitacao import Solicitacao
from ...models.status_local import StatusLocal

class SolicitacaoSqliteProvider(SolicitacaoProviderInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def criar_solicitacao(self, solicitacao: Dict[str, Any]) -> Dict[str, Any]:
        nova_solic = Solicitacao(
            id=str(uuid.uuid4())[:8],
            tipo=solicitacao.get('tipo', 'INSERIR'),
            especialidade=solicitacao.get('especialidade', ''),
            procedimento=solicitacao.get('procedimento', ''),
            codigo_paciente=int(solicitacao.get('codigo_paciente', 0)),
            nome_paciente=solicitacao.get('nome_paciente', ''),
            judicializado=solicitacao.get('judicializado', 'Não'),
            swallis=solicitacao.get('swallis', ''),
            medico_responsavel=solicitacao.get('medico_responsavel', ''),
            detalhes=solicitacao.get('detalhes', ''),
            tempo_standby=int(solicitacao.get('tempo_standby')) if solicitacao.get('tempo_standby') else None,
            status='PENDENTE',
            data_criacao=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            perfil_executor=solicitacao.get('perfil_executor', ''),
            procedimento_anterior=solicitacao.get('procedimento_anterior', '')
        )
        
        self.session.add(nova_solic)
        await self.session.commit()
        
        # Retorna o dicionário
        return {
            'id': nova_solic.id,
            'tipo': nova_solic.tipo,
            'especialidade': nova_solic.especialidade,
            'procedimento': nova_solic.procedimento,
            'codigo_paciente': nova_solic.codigo_paciente,
            'nome_paciente': nova_solic.nome_paciente,
            'judicializado': nova_solic.judicializado,
            'swallis': nova_solic.swallis,
            'medico_responsavel': nova_solic.medico_responsavel,
            'detalhes': nova_solic.detalhes,
            'tempo_standby': nova_solic.tempo_standby,
            'status': nova_solic.status,
            'data_criacao': nova_solic.data_criacao,
            'perfil_executor': nova_solic.perfil_executor,
            'procedimento_anterior': nova_solic.procedimento_anterior
        }

    async def listar_solicitacoes(self) -> List[Dict[str, Any]]:
        stmt = select(Solicitacao)
        result = await self.session.execute(stmt)
        solicitacoes = result.scalars().all()
        
        return [
            {
                'id': s.id,
                'tipo': s.tipo,
                'especialidade': s.especialidade,
                'procedimento': s.procedimento,
                'codigo_paciente': s.codigo_paciente,
                'nome_paciente': s.nome_paciente,
                'judicializado': s.judicializado,
                'swallis': s.swallis,
                'medico_responsavel': s.medico_responsavel,
                'detalhes': s.detalhes,
                'tempo_standby': s.tempo_standby,
                'status': s.status,
                'data_criacao': s.data_criacao,
                'perfil_executor': s.perfil_executor,
                'procedimento_anterior': s.procedimento_anterior
            }
            for s in solicitacoes
        ]

    async def atualizar_status_solicitacao(self, id_solicitacao: str, novo_status: str) -> Dict[str, Any]:
        stmt = select(Solicitacao).where(Solicitacao.id == id_solicitacao)
        result = await self.session.execute(stmt)
        solic = result.scalar_one_or_none()
        
        if not solic:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitação não encontrada no SQLite")
            
        solic.status = novo_status.upper()
        await self.session.commit()
        
        return {
            'id': solic.id,
            'tipo': solic.tipo,
            'especialidade': solic.especialidade,
            'procedimento': solic.procedimento,
            'codigo_paciente': solic.codigo_paciente,
            'nome_paciente': solic.nome_paciente,
            'judicializado': solic.judicializado,
            'swallis': solic.swallis,
            'medico_responsavel': solic.medico_responsavel,
            'detalhes': solic.detalhes,
            'tempo_standby': solic.tempo_standby,
            'status': solic.status,
            'data_criacao': solic.data_criacao,
            'perfil_executor': solic.perfil_executor,
            'procedimento_anterior': solic.procedimento_anterior
        }

    async def salvar_status_local_paciente(self, codigo_paciente: str, status_local: str) -> Dict[str, Any]:
        cod_paciente_int = int(codigo_paciente)
        stmt = select(StatusLocal).where(StatusLocal.codigo_paciente == cod_paciente_int)
        result = await self.session.execute(stmt)
        s_local = result.scalar_one_or_none()
        
        data_atualizacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if s_local:
            s_local.status_local = status_local
            s_local.data_atualizacao = data_atualizacao
        else:
            s_local = StatusLocal(
                codigo_paciente=cod_paciente_int,
                status_local=status_local,
                data_atualizacao=data_atualizacao
            )
            self.session.add(s_local)
            
        await self.session.commit()
        
        return {
            'codigo_paciente': codigo_paciente,
            'status_local': status_local,
            'data_atualizacao': data_atualizacao
        }

    async def obter_status_locais_pacientes(self) -> Dict[str, str]:
        stmt = select(StatusLocal)
        result = await self.session.execute(stmt)
        status_list = result.scalars().all()
        return {str(s.codigo_paciente): s.status_local for s in status_list}
